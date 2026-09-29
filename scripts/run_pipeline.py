#!/usr/bin/env python3
"""Create an immutable-file manifest, identify exact duplicates, and gate JSON records.

Uses only Python's standard library so it is runnable before external source systems exist.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import shutil
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG = ROOT / "configs" / "sources" / "sources.json"
SCHEMAS = ROOT / "schemas"


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def output_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def visible_files(roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        found.extend(item for item in root.rglob("*") if item.is_file() and item.name != ".gitkeep")
    return sorted(found)


def file_manifest(roots: list[Path]) -> list[dict[str, Any]]:
    result = []
    for path in visible_files(roots):
        mime, _ = mimetypes.guess_type(path.name)
        relative = path.relative_to(ROOT).as_posix()
        result.append({
            "file_id": "FILE-" + sha256(path)[:16].upper(),
            "relative_path": relative,
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
            "mime_type": mime or "application/octet-stream",
            "extension": path.suffix.lower(),
            "source_id": "",  # populated by later collector/sidecar metadata integration
            "archived_at": now(),
        })
    return result


def duplicates(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in manifest:
        grouped[entry["sha256"]].append(entry)
    return [
        {"sha256": digest, "kind": "exact_content_duplicate", "files": files,
         "recommended_action": "retain all raw originals; review provenance and reference one canonical copy downstream"}
        for digest, files in grouped.items() if len(files) > 1
    ]


def record_issues(record: dict[str, Any], schema: dict[str, Any], source_ids: set[str], path: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    record_name = path.relative_to(ROOT).as_posix()
    def add(level: str, field: str, message: str) -> None:
        issues.append({"level": level, "record": record_name, "record_id": str(record.get("record_id", "")), "field": field, "message": message})

    for field in schema.get("required", []):
        if field not in record or record[field] in (None, "", []):
            add("ERROR", field, "required field is missing or empty")
    for field, rules in schema.get("properties", {}).items():
        if field not in record:
            continue
        value = record[field]
        expected = rules.get("type")
        types = {"string": str, "object": dict, "array": list, "integer": int}
        if expected in types and (not isinstance(value, types[expected]) or (expected == "integer" and isinstance(value, bool))):
            add("ERROR", field, f"expected {expected}")
        if "enum" in rules and value not in rules["enum"]:
            add("ERROR", field, f"value must be one of: {', '.join(rules['enum'])}")
        if "const" in rules and value != rules["const"]:
            add("ERROR", field, f"value must equal {rules['const']}")
        if isinstance(value, list) and rules.get("minItems") and len(value) < rules["minItems"]:
            add("ERROR", field, f"must contain at least {rules['minItems']} item(s)")
    source_id = record.get("source_id")
    if source_id and source_id not in source_ids:
        add("ERROR", "source_id", f"unknown source_id: {source_id}")
    if record.get("record_type") == "model":
        evidence = record.get("evidence", [])
        for index, item in enumerate(evidence if isinstance(evidence, list) else []):
            if not isinstance(item, dict):
                add("ERROR", f"evidence[{index}]", "must be an object")
                continue
            for key in ("field", "quote", "locator"):
                if not item.get(key):
                    add("ERROR", f"evidence[{index}].{key}", "evidence needs field, quote and locator")
        if record.get("record_status") in ("reviewed", "approved") and not evidence:
            add("ERROR", "evidence", "reviewed/approved model record requires evidence")
    if record.get("record_type") == "dataset" and record.get("sample_validation_status") == "passed":
        if not record.get("sample_count"):
            add("WARNING", "sample_count", "passed sample validation should state sample_count")
    if record.get("license_status") == "unknown":
        add("WARNING", "license_status", "license must be reviewed before redistribution or curated publication")
    if record.get("record_status") == "draft":
        add("INFO", "record_status", "draft record has not received human review")
    return issues


def validate_records(record_roots: list[Path], source_ids: set[str]) -> tuple[list[dict[str, str]], int]:
    issues: list[dict[str, str]] = []
    count = 0
    schemas = {p.stem.replace(".schema", ""): load_json(p) for p in SCHEMAS.glob("*.schema.json")}
    for path in visible_files(record_roots):
        if path.suffix.lower() != ".json":
            issues.append({"level": "ERROR", "record": path.relative_to(ROOT).as_posix(), "record_id": "", "field": "file", "message": "record must be a JSON file"})
            continue
        try:
            record = load_json(path)
        except json.JSONDecodeError as exc:
            issues.append({"level": "ERROR", "record": path.relative_to(ROOT).as_posix(), "record_id": "", "field": "file", "message": f"invalid JSON: {exc.msg}"})
            continue
        count += 1
        key = {"model": "model_record", "dataset": "dataset_card", "relation": "relation_record", "conflict": "conflict_record"}.get(record.get("record_type"))
        if not key or key not in schemas:
            issues.append({"level": "ERROR", "record": path.relative_to(ROOT).as_posix(), "record_id": str(record.get("record_id", "")), "field": "record_type", "message": "unknown record_type"})
            continue
        issues.extend(record_issues(record, schemas[key], source_ids, path))
    return issues, count


def markdown_report(summary: dict[str, Any], issues: list[dict[str, str]], duplicate_groups: list[dict[str, Any]]) -> str:
    lines = ["# 数据质量门禁报告", "", f"- 生成时间（UTC）：{summary['generated_at']}", f"- 扫描文件：{summary['files_scanned']}", f"- 完全重复组：{len(duplicate_groups)}", f"- 校验记录：{summary['records_validated']}", "", "## 质量结果", "", "| 级别 | 数量 |", "| --- | ---: |"]
    for level in ("ERROR", "WARNING", "INFO"):
        lines.append(f"| {level} | {summary['issue_counts'].get(level, 0)} |")
    lines.extend(["", "## 问题明细", ""])
    if not issues:
        lines.append("无问题。")
    else:
        lines.extend(["| 级别 | 记录 | 字段 | 说明 |", "| --- | --- | --- | --- |"])
        for item in issues:
            lines.append("| {level} | {record} | {field} | {message} |".format(**item))
    lines.extend(["", "## 重复文件", ""])
    if not duplicate_groups:
        lines.append("未发现完全重复文件。")
    else:
        for group in duplicate_groups:
            lines.append(f"- `{group['sha256']}`：" + "，".join(f"`{x['relative_path']}`" for x in group["files"]))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run archive manifest, exact duplicate and record quality checks.")
    parser.add_argument("--include-fixtures", action="store_true", help="Include demonstration files and records under fixtures/.")
    parser.add_argument("--input-root", action="append", default=[], metavar="PATH", help="Additional file root to archive and hash (repeatable; paths must be inside the project root).")
    parser.add_argument("--clean", action="store_true", help="Remove previous generated manifest/report outputs before running.")
    args = parser.parse_args()
    if args.clean:
        # Only remove artifacts owned by this pipeline. Governance dashboards and
        # collection reports share data/reports/ and must survive a quality rerun.
        for directory, names in ((DATA / "manifests", {"file_manifest.jsonl", "file_manifest.csv", "duplicates.json"}), (DATA / "reports", {"quality_report.json", "quality_report.md", "pipeline_summary.json"})):
            for name in names:
                child = directory / name
                if child.exists():
                    if child.is_file(): child.unlink()
                    elif child.is_dir(): shutil.rmtree(child)
    external_roots = [(ROOT / value).resolve() if not Path(value).is_absolute() else Path(value).resolve() for value in args.input_root]
    try:
        for path in external_roots:
            path.relative_to(ROOT)
    except ValueError as exc:
        parser.error(f"--input-root must be inside project root: {exc}")
    raw_roots = [DATA / "raw", *external_roots] + ([ROOT / "fixtures" / "raw"] if args.include_fixtures else [])
    record_roots = [DATA / "records" / "imported", DATA / "records" / "relations", DATA / "records" / "conflicts"] + ([ROOT / "fixtures" / "records"] if args.include_fixtures else [])
    manifest = file_manifest(raw_roots)
    duplicate_groups = duplicates(manifest)
    sources = load_json(CONFIG)
    source_ids = {item["source_id"] for item in sources}
    issues, record_count = validate_records(record_roots, source_ids)
    counts = {level: sum(1 for issue in issues if issue["level"] == level) for level in ("ERROR", "WARNING", "INFO")}
    summary = {"generated_at": now(), "include_fixtures": args.include_fixtures, "input_roots": [path.relative_to(ROOT).as_posix() for path in external_roots], "files_scanned": len(manifest), "exact_duplicate_groups": len(duplicate_groups), "records_validated": record_count, "issue_counts": counts, "gate_status": "FAIL" if counts["ERROR"] else "PASS_WITH_WARNINGS" if counts["WARNING"] else "PASS"}
    manifests = DATA / "manifests"
    reports = DATA / "reports"
    manifests.mkdir(parents=True, exist_ok=True); reports.mkdir(parents=True, exist_ok=True)
    with (manifests / "file_manifest.jsonl").open("w", encoding="utf-8") as handle:
        for row in manifest: handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (manifests / "file_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file_id", "relative_path", "sha256", "size_bytes", "mime_type", "extension", "source_id", "archived_at"])
        writer.writeheader(); writer.writerows(manifest)
    output_json(manifests / "duplicates.json", duplicate_groups)
    output_json(reports / "quality_report.json", {"summary": summary, "issues": issues})
    output_json(reports / "pipeline_summary.json", summary)
    (reports / "quality_report.md").write_text(markdown_report(summary, issues, duplicate_groups), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if counts["ERROR"] else 0

if __name__ == "__main__":
    sys.exit(main())
