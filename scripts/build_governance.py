#!/usr/bin/env python3
"""Build governance artifacts from normalized member deliveries.

This does not claim to re-download or independently validate source datasets. It
registers evidence available locally, derives query relations, records declared
conflicts, and audits reproducibility evidence supplied by member two.
"""
from __future__ import annotations

import hashlib
import html
import json
import shutil
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATASETS = ROOT / "datasets"
RECORDS = DATA / "records" / "imported"
RELATIONS = DATA / "records" / "relations"
CONFLICTS = DATA / "records" / "conflicts"
NORMALIZED = DATA / "normalized"
REPORTS = DATA / "reports"
MANIFESTS = DATA / "manifests"


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def slug(value: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in value.upper()).strip("-")


def file_manifest() -> list[dict[str, Any]]:
    files = [p for p in DATASETS.rglob("*") if p.is_file() and p.name != ".DS_Store"]
    rows = []
    for p in sorted(files):
        category = "member1_delivery" if "member1_model_research" in p.parts else "member2_delivery"
        rows.append({"delivery_file_id": "DELIVERY-" + sha(p)[:16].upper(), "relative_path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "size_bytes": p.stat().st_size, "category": category, "preservation": "read_only_source_delivery"})
    return rows


def relations(models: list[dict], datasets: list[dict]) -> list[dict]:
    rows = []
    def add(subject: str, predicate: str, obj: str, source: str, quote: str, locator: str) -> None:
        rows.append({"record_id": f"REL-{slug(subject)}-{predicate.upper()}-{slug(obj)}", "record_type": "relation", "subject_id": subject, "predicate": predicate, "object_id": obj, "source_id": source, "evidence_quote": quote, "evidence_locator": locator, "record_status": "reviewed"})
    for model in models:
        model_id = model["record_id"]
        add("ORG-" + slug(model["manufacturer"]), "manufactures", model_id, model["source_id"], f"{model['manufacturer']} {model['model']} model record imported from member-one delivery.", "member-one model table")
        for band in model.get("communication_bands", []): add(model_id, "uses_protocol", "BAND-" + slug(band), model["source_id"], band, "member-one model table > 通信频段")
        for protocol in model.get("communication_protocols", []): add(model_id, "uses_protocol", "PROTOCOL-" + slug(protocol), model["source_id"], protocol, "member-one model table > 图传/通信协议")
        for sdk in model.get("sdk", []): add(model_id, "supports_sdk", "SDK-" + slug(sdk), model["source_id"], sdk, "member-one model table > SDK/开发接口")
        for firmware in model.get("firmware", []): add(model_id, "has_firmware", "FIRMWARE-" + slug(firmware), model["source_id"], firmware, "member-one model table > 固件信息")
    for dataset in datasets:
        dataset_id = dataset["record_id"]
        for modality in dataset.get("modalities", []): add(dataset_id, "contains_component", "MODALITY-" + slug(modality), dataset["source_id"], modality, "member-two dataset card > modalities")
    return rows


def reproducibility_audit() -> list[dict[str, Any]]:
    root = DATASETS / "member2_multimodal_datasets" / "validation_records"
    result = []
    for directory in sorted(p for p in root.iterdir() if p.is_dir()):
        files = sorted(directory.glob("*.json"))
        parsed, hash_records, status_records, caveats = [], [], [], []
        for path in files:
            try:
                data = read_json(path); parsed.append(path.relative_to(ROOT).as_posix())
            except json.JSONDecodeError:
                continue
            for key in ("sha256", "expected_size", "actual_size", "download_status", "zip_integrity", "rar_integrity", "final_result", "problems", "limitations"):
                if key in data:
                    if key == "sha256": hash_records.append({"file": path.name, "sha256": data[key]})
                    elif key in {"problems", "limitations"}: caveats.append({"file": path.name, "key": key, "value": data[key]})
                    else: status_records.append({"file": path.name, "key": key, "value": data[key]})
        status = "AUDITABLE_NOT_INDEPENDENTLY_REPRODUCED" if parsed else "INSUFFICIENT_LOCAL_EVIDENCE"
        result.append({"dataset": directory.name, "audit_scope": "local member-two validation records only", "status": status, "parsed_json_records": parsed, "declared_hashes": hash_records, "declared_validation_status": status_records, "caveats": caveats, "independent_download_or_file_read_performed_by_person4": False, "conclusion": "Supplied records are parseable and retain declared validation evidence. Local raw sample payloads are absent, so their hash, format, size, and conclusion cannot be independently reproduced in this run."})
    return result


def dashboard(summary: dict[str, Any]) -> str:
    def li(values: list[str]) -> str: return "".join(f"<li>{html.escape(value)}</li>" for value in values)
    models = summary["model_progress"]
    datasets = summary["datasets"]
    return f"""<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>无人机数据治理看板</title><style>body{{font:15px system-ui;margin:32px;max-width:1200px;color:#15222e}}h1{{margin-bottom:4px}}.cards{{display:flex;gap:14px;flex-wrap:wrap}}.card{{background:#eef4f8;border-radius:8px;padding:16px;min-width:155px}}.n{{font-size:28px;font-weight:700}}table{{border-collapse:collapse;width:100%;margin:14px 0}}th,td{{padding:9px;border-bottom:1px solid #d7e0e7;text-align:left}}.risk{{color:#a21d1d;font-weight:700}}small{{color:#52636f}}</style><h1>无人机资料与多模态数据治理看板</h1><small>生成时间：{html.escape(summary['generated_at'])}；只基于成员一、二本地交付，非原始数据集独立复现结论。</small><div class='cards'><div class='card'><div class='n'>{summary['models_imported']}</div>型号记录</div><div class='card'><div class='n'>{summary['datasets_imported']}</div>数据集卡</div><div class='card'><div class='n'>{summary['evidence_count']}</div>型号证据</div><div class='card'><div class='n'>{summary['source_count']}</div>来源</div><div class='card'><div class='n'>{summary['delivery_file_count']}</div>交付文件</div></div><h2>型号采集进度</h2><table><tr><th>厂商</th><th>型号</th><th>完成度</th><th>待补内容</th></tr>{''.join(f"<tr><td>{html.escape(x['厂商'])}</td><td>{html.escape(x['型号'])}</td><td>{html.escape(x.get('完成度',''))}</td><td class='risk'>{html.escape(x.get('待补内容',''))}</td></tr>" for x in models)}</table><h2>数据集与许可</h2><table><tr><th>数据集</th><th>模态</th><th>许可状态</th><th>验证状态</th></tr>{''.join(f"<tr><td>{html.escape(x['dataset_name'])}</td><td>{html.escape(', '.join(x['modalities']))}</td><td class='risk'>{html.escape(x['license_status'])}</td><td>{html.escape(x['sample_validation_status'])}</td></tr>" for x in datasets)}</table><h2>治理缺口</h2><ul>{li(summary['known_gaps'])}</ul><h2>解释边界</h2><ul><li>人员二的下载、解压和跨模态结论以其验证记录为准；本次仅完成本地记录审计。</li><li>原始全量数据、原始小样本和受限许可文件未复制进仓库。</li><li>FCC / FAA 原始查询结果仍是四个型号的主要缺口。</li></ul></html>"""


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Build governance, provenance, relation, conflict and reproducibility artifacts.")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    if args.clean:
        for path in (RELATIONS, CONFLICTS, DATA / "delivery_manifest.json", DATA / "reproducibility_audit.json", REPORTS / "governance_dashboard.html"): 
            if path.is_dir(): shutil.rmtree(path)
            elif path.exists(): path.unlink()
    models = [read_json(p) for p in sorted((RECORDS / "models").glob("*.json"))]
    datasets = [read_json(p) for p in sorted((RECORDS / "datasets").glob("*.json"))]
    evidence = [json.loads(line) for line in (NORMALIZED / "evidence.jsonl").read_text(encoding="utf-8").splitlines() if line]
    progress = read_json(NORMALIZED / "collection_progress.json")
    sources = read_json(ROOT / "configs" / "sources" / "sources.json")
    rels = relations(models, datasets)
    for row in rels: write_json(RELATIONS / f"{row['record_id']}.json", row)
    mmaud_sources = [x["source_id"] for x in sources if "MMAUD" in x["source_id"]]
    conflicts = [
        {"record_id": "CONFLICT-DATASET-MMAUD-FULL-NAME-001", "record_type": "conflict", "entity_id": "DATASET-MMAUD", "field": "basic_info.full_name", "conflicting_values": [{"value": value["value"], "source_url": value["source_url"]} for value in read_json(DATASETS / "member2_multimodal_datasets" / "dataset_cards" / "MMAUD.json")["basic_info"]["full_name_conflict"]], "source_ids": mmaud_sources[:2], "status": "open", "resolution": "Retain both official/paper titles; select display name by use context."},
        {"record_id": "CONFLICT-DATASET-MMAUD-READINESS-001", "record_type": "conflict", "entity_id": "DATASET-MMAUD", "field": "validation.readiness", "conflicting_values": [{"value": "CROSS_MODAL_READY", "source": "member2 dataset_summary.csv"}, {"value": "NOT_READY", "source": "MMAUD_sample_validation.json (earlier limited sample check)"}, {"value": "READY_FOR_FINAL_DATASET_EVALUATION=YES", "source": "MMAUD_cross_modal_validation.json (UG2+ derived validation subset)"}], "source_ids": mmaud_sources[:2], "status": "accepted_difference", "resolution": "Scope differs: the limited raw-sample check was blocked, while the later UG2+ derived subset supports partial cross-modal assessment. Keep subset/scope with every readiness claim; do not represent full MMAUD as independently reproduced."}
    ]
    for row in conflicts: write_json(CONFLICTS / f"{row['record_id']}.json", row)
    delivery = file_manifest(); write_json(DATA / "delivery_manifest.json", delivery)
    audit = reproducibility_audit(); write_json(DATA / "reproducibility_audit.json", audit)
    summary = {"generated_at": now(), "models_imported": len(models), "datasets_imported": len(datasets), "evidence_count": len(evidence), "source_count": len(sources), "relation_count": len(rels), "conflict_count": len(conflicts), "delivery_file_count": len(delivery), "delivery_total_bytes": sum(x["size_bytes"] for x in delivery), "model_progress": progress, "datasets": datasets, "known_gaps": [x.get("待补内容", "") for x in progress if x.get("待补内容")], "license_counts": dict(Counter(x["license_status"] for x in datasets)), "reproducibility_status": {x["dataset"]: x["status"] for x in audit}}
    write_json(NORMALIZED / "governance_dashboard_data.json", summary)
    (REPORTS / "governance_dashboard.html").write_text(dashboard(summary), encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("models_imported", "datasets_imported", "evidence_count", "source_count", "relation_count", "conflict_count", "delivery_file_count", "reproducibility_status")}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
