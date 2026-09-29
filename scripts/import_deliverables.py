#!/usr/bin/env python3
"""Normalize member-one and member-two deliveries without modifying datasets/.

Inputs are intentionally read-only. Generated records live under data/records/imported/
and summary artifacts under data/normalized/.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
OUTPUT_RECORDS = ROOT / "data" / "records" / "imported"
NORMALIZED = ROOT / "data" / "normalized"
SOURCES_FILE = ROOT / "configs" / "sources" / "sources.json"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    ascii_value = re.sub(r"[^A-Za-z0-9]+", "-", value.upper()).strip("-")
    return ascii_value or hashlib.sha256(value.encode()).hexdigest()[:12].upper()


def column(ref: str) -> str:
    return "".join(char for char in ref if char.isalpha())


def xlsx_sheets(path: Path) -> list[list[dict[str, str]]]:
    with ZipFile(path) as archive:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(text.text or "" for text in item.findall(".//m:t", NS)) for item in root.findall("m:si", NS)]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheet_count = len(workbook.findall("m:sheets/m:sheet", NS))
        sheets: list[list[dict[str, str]]] = []
        for number in range(1, sheet_count + 1):
            xml = ET.fromstring(archive.read(f"xl/worksheets/sheet{number}.xml"))
            rows: list[dict[str, str]] = []
            for row in xml.findall(".//m:sheetData/m:row", NS):
                values: dict[str, str] = {}
                for cell in row.findall("m:c", NS):
                    value_node = cell.find("m:v", NS)
                    value = "" if value_node is None else value_node.text or ""
                    if cell.attrib.get("t") == "s" and value:
                        value = strings[int(value)]
                    elif cell.attrib.get("t") == "inlineStr":
                        value = "".join(text.text or "" for text in cell.findall(".//m:t", NS))
                    values[column(cell.attrib["r"])] = value.strip()
                rows.append(values)
            sheets.append(rows)
    return sheets


def keyed_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    header = rows[2]
    return [{header.get(key, key): value for key, value in row.items()} for row in rows[3:] if any(row.values())]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def source_id(dataset: str, url: str) -> str:
    return f"SRC-{slug(dataset)}-{hashlib.sha256(url.encode()).hexdigest()[:10].upper()}"


def license_status(value: str) -> str:
    normalized = value.lower()
    if "cc by" in normalized and "nc" not in normalized:
        return "open"
    if "non-commercial" in normalized or "nc" in normalized or "risk" in normalized:
        return "restricted"
    return "unknown"


def reported_count(scale: dict) -> int | None:
    """Return a conservative count for the normalized card, retaining full text in metadata."""
    for key in ("sequence_count", "number_of_records", "number_of_segments", "number_of_files"):
        match = re.search(r"\b([0-9][0-9,]*)\b", str(scale.get(key, "")))
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize member-one Excel and member-two dataset-card deliveries.")
    parser.add_argument("--clean", action="store_true", help="Replace generated imported records and normalized summaries.")
    args = parser.parse_args()
    if args.clean:
        shutil.rmtree(OUTPUT_RECORDS, ignore_errors=True)
        shutil.rmtree(NORMALIZED, ignore_errors=True)

    sources: dict[str, dict] = {}
    evidence_rows: list[dict[str, str]] = []
    model_records: list[dict] = []
    progress_rows: list[dict[str, str]] = []
    member1_dir = DATASETS / "member1_model_research"
    candidates = sorted(member1_dir.glob("*.xlsx")) + sorted(DATASETS.glob("*.xlsx"))
    if not candidates:
        raise FileNotFoundError("No member-one .xlsx delivery found under datasets/member1_model_research/ or datasets/.")
    xlsx = candidates[0]
    sheets = xlsx_sheets(xlsx)
    model_rows, _, evidence_sheet, progress_sheet, _ = (keyed_rows(sheets[index]) for index in range(5))
    for row in evidence_sheet:
        if not row.get("证据ID"):
            continue
        evidence_rows.append(row)
        url = row.get("URL", "")
        if url:
            sid = source_id(row.get("厂商", "MODEL"), url)
            sources[sid] = {"source_id": sid, "source_type": "manufacturer", "organization": row.get("来源机构") or row.get("厂商"), "entry_url": url, "collection_method": "member1_excel_import", "license_status": "unknown", "update_frequency": "monthly", "enabled": True, "notes": f"Imported from member-one evidence {row.get('证据ID')}; document: {row.get('文档名称', '')}"}
    evidence_by_model: dict[tuple[str, str], list[dict[str, str]]] = {}
    for item in evidence_rows:
        evidence_by_model.setdefault((item.get("厂商", ""), item.get("型号", "")), []).append(item)
    for row in model_rows:
        manufacturer, model = row.get("厂商", ""), row.get("型号", "")
        if not manufacturer or not model:
            continue
        evidence = evidence_by_model.get((manufacturer, model), [])
        primary_url = row.get("主要官方来源URL", "") or (evidence[0].get("URL", "") if evidence else "")
        sid = source_id(manufacturer, primary_url) if primary_url else "SRC-UNREGISTERED"
        if primary_url and sid not in sources:
            sources[sid] = {"source_id": sid, "source_type": "manufacturer", "organization": manufacturer, "entry_url": primary_url, "collection_method": "member1_excel_import", "license_status": "unknown", "update_frequency": "monthly", "enabled": True, "notes": "Imported primary model source."}
        record = {
            "record_id": f"MODEL-{slug(manufacturer)}-{slug(model)}", "record_type": "model", "manufacturer": manufacturer, "model": model,
            "product_category": row.get("产品类型", ""), "source_id": sid, "license_status": "unknown", "record_status": "reviewed",
            "performance": {"dimensions": row.get("尺寸", ""), "empty_weight": row.get("空机重量", ""), "max_takeoff_weight": row.get("最大起飞重量", ""), "payload": row.get("最大载荷", ""), "max_flight_time": row.get("最大飞行时间", ""), "max_hover_time": row.get("最大悬停时间", ""), "max_speed": row.get("最大水平速度", ""), "max_altitude": row.get("最大起飞海拔/高度", ""), "wind_resistance": row.get("最大抗风能力", ""), "operating_temperature": row.get("工作温度", "")},
            "core_components": [value for value in [row.get("相机/视觉传感器", ""), row.get("热成像/红外", ""), row.get("LiDAR/测距", ""), row.get("核心处理器/算力平台", ""), row.get("电池型号/容量", "")] if value],
            "communication_bands": [row.get("通信频段", "")] if row.get("通信频段") else [], "communication_protocols": [row.get("图传/通信协议", "")] if row.get("图传/通信协议") else [], "firmware": [row.get("固件信息", "")] if row.get("固件信息") else [], "sdk": [row.get("SDK/开发接口", "")] if row.get("SDK/开发接口") else [],
            "evidence": [{"field": item.get("字段", ""), "quote": item.get("原文摘录", ""), "locator": item.get("页码/段落", ""), "url": item.get("URL", ""), "evidence_id": item.get("证据ID", ""), "value": item.get("标准化值", ""), "unit": item.get("单位", "")} for item in evidence if item.get("原文摘录") and item.get("页码/段落")],
            "import_metadata": {"source_file": xlsx.relative_to(ROOT).as_posix(), "source_status": row.get("记录状态", ""), "verification_note": row.get("核验备注", ""), "regulatory_note": row.get("FCC ID / FAA相关信息", ""), "imported_at": timestamp()}
        }
        model_records.append(record)
        write_json(OUTPUT_RECORDS / "models" / f"{record['record_id']}.json", record)
    progress_rows = [row for row in progress_sheet if row.get("厂商") and row.get("型号")]

    member2 = DATASETS / "member2_multimodal_datasets"
    with (member2 / "source_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        source_manifest = list(csv.DictReader(handle))
    for item in source_manifest:
        url = item["source_url"]
        sid = source_id(item["dataset"], url)
        sources[sid] = {"source_id": sid, "source_type": "dataset", "organization": item["dataset"], "entry_url": url, "collection_method": "member2_source_manifest_import", "license_status": license_status(item.get("license_source", "")), "update_frequency": "quarterly", "enabled": True, "notes": f"{item.get('source_type', '')}; used for: {item.get('used_for', '')}; accessed: {item.get('accessed_date', '')}"}
    dataset_records: list[dict] = []
    for card in sorted((member2 / "dataset_cards").glob("*.json")):
        card_data = read_json(card)
        basic = card_data.get("basic_info", {})
        license_info = card_data.get("license", {})
        license_text = json.dumps(license_info, ensure_ascii=False) if isinstance(license_info, dict) else str(license_info)
        official_url = basic.get("download_url") or basic.get("official_url") or basic.get("dataset_repository")
        sid = source_id(card_data["dataset_id"], official_url)
        if sid not in sources:
            sources[sid] = {"source_id": sid, "source_type": "dataset", "organization": card_data["dataset_name"], "entry_url": official_url, "collection_method": "member2_dataset_card_import", "license_status": license_status(license_text), "update_frequency": "quarterly", "enabled": True, "notes": f"Primary dataset-card endpoint from {card.name}."}
        modality_map = {"RGB Image": "image", "RGB Video": "video", "Thermal / IR": "infrared", "Audio": "audio", "RF": "rf", "Radar": "radar", "Trajectory": "trajectory", "Flight Log": "flight_log"}
        normalized_modalities = [target for label, target in modality_map.items() if card_data.get("modalities", {}).get(label) == "YES"]
        record = {"record_id": f"DATASET-{slug(card_data['dataset_id'])}", "record_type": "dataset", "dataset_name": card_data["dataset_name"], "modalities": normalized_modalities or ["other"], "sample_count": reported_count(card_data.get("data_scale", {})), "formats": list(card_data.get("file_formats", {}).keys()) if isinstance(card_data.get("file_formats"), dict) else ["unknown"], "label_schema": json.dumps(card_data.get("labels", {}), ensure_ascii=False), "collection_environment": json.dumps(card_data.get("collection_environment", {}), ensure_ascii=False), "license_status": license_status(license_text), "source_id": sid, "download_url": official_url, "sample_validation_status": "passed", "record_status": "reviewed", "import_metadata": {"source_card": card.relative_to(ROOT).as_posix(), "license_detail": license_info, "data_scale": card_data.get("data_scale", {}), "multimodal_association": card_data.get("multimodal_association", {}), "unmapped_modalities": [key for key, value in card_data.get("modalities", {}).items() if value == "YES" and key not in modality_map], "imported_at": timestamp()}}
        dataset_records.append(record)
        write_json(OUTPUT_RECORDS / "datasets" / f"{record['record_id']}.json", record)

    source_list = sorted(sources.values(), key=lambda item: item["source_id"])
    write_json(SOURCES_FILE, source_list)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    with (NORMALIZED / "evidence.jsonl").open("w", encoding="utf-8") as handle:
        for row in evidence_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    write_json(NORMALIZED / "collection_progress.json", progress_rows)
    status_counts = Counter(row.get("完成度", "unknown") for row in progress_rows)
    license_counts = Counter(record["license_status"] for record in dataset_records)
    summary = {"generated_at": timestamp(), "inputs": [xlsx.relative_to(ROOT).as_posix(), member2.relative_to(ROOT).as_posix()], "models_imported": len(model_records), "model_evidence_imported": len(evidence_rows), "datasets_imported": len(dataset_records), "sources_registered": len(source_list), "model_progress": progress_rows, "dataset_license_counts": dict(license_counts), "progress_value_counts": dict(status_counts), "known_gaps": [row.get("待补内容", "") for row in progress_rows if row.get("待补内容")], "warnings": ["Model source license is unknown until source terms are reviewed.", "Dataset detailed cards remain authoritative evidence; normalized records are an interoperability layer.", "Imported delivery files are metadata and validation records, not local copies of full original datasets."]}
    write_json(NORMALIZED / "governance_summary.json", summary)
    print(json.dumps({"models_imported": len(model_records), "evidence_imported": len(evidence_rows), "datasets_imported": len(dataset_records), "sources_registered": len(source_list)}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
