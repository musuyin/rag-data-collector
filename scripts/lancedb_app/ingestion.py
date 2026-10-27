"""Read-only input planning, disk-backed validation, and bounded LanceDB batches."""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import tempfile
import uuid
from pathlib import Path

from .records import MAX_RECORD_BYTES, ROOT, ConflictError, RecordError, Validator, canonical
from .store import Store, now


def file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def input_files(paths: list[Path]) -> list[Path]:
    result = set()
    for path in paths:
        if not path.exists():
            raise RecordError(f"输入不存在：{path}")
        if path.is_dir():
            result.update(p.resolve() for p in path.rglob("*") if p.is_file() and p.suffix.lower() in {
                ".json", ".jsonl", ".csv"
            })
        elif path.suffix.lower() in {".json", ".jsonl", ".csv"}:
            result.add(path.resolve())
        else:
            raise RecordError("仅支持 JSON、JSONL 和带表头的 CSV。")
    if not result:
        raise RecordError("没有找到可导入文件。")
    return sorted(result)


def read_records(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        if path.suffix.lower() == ".json":
            if path.stat().st_size > 64 * 1024 * 1024:
                raise RecordError("单个 JSON 文件上限 64 MiB；大批量数据请使用 JSONL。")
            value = json.load(stream)
            for index, body in enumerate(value if isinstance(value, list) else [value], 1):
                yield f"json:{index}", body
        elif path.suffix.lower() == ".jsonl":
            index = 0
            while line := stream.readline(MAX_RECORD_BYTES + 1):
                index += 1
                if len(line) > MAX_RECORD_BYTES:
                    raise RecordError(f"JSONL 第 {index} 行过长，请拆成独立的小记录。")
                if line.strip():
                    yield f"line:{index}", json.loads(line)
        else:
            csv.field_size_limit(MAX_RECORD_BYTES)
            reader = csv.DictReader(stream)
            if (not reader.fieldnames or any(not name.strip() for name in reader.fieldnames)
                    or len(reader.fieldnames) != len(set(reader.fieldnames))):
                raise RecordError("CSV 必须有非重复表头。")
            for body in reader:
                if None in body or any(value is None for value in body.values()):
                    raise RecordError(f"CSV 第 {reader.line_num} 行列数与表头不符。")
                for key, value in body.items():
                    if value.lstrip().startswith(("[", "{")) or key == "sample_count":
                        body[key] = json.loads(value)
                yield f"csv-line:{reader.line_num}", body


def source_label(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        # Do not write a user's private absolute input path into portable receipts.
        return path.name


class Plan:
    """Temporary validated snapshot. No database or persistent state is created during dry runs."""
    def __init__(self, paths: list[Path], validator: Validator):
        self.tmp = tempfile.TemporaryDirectory(prefix="lancedb-plan-")
        self.spool = sqlite3.connect(Path(self.tmp.name) / "plan.sqlite3")
        self.spool.execute("CREATE TABLE entries (id TEXT PRIMARY KEY, entry TEXT NOT NULL)")
        self.summary = {"files": [], "records": 0, "license_counts": {}}
        try:
            for path in input_files(paths):
                before = file_hash(path)
                count = 0
                locator = "file"
                try:
                    for locator, raw in read_records(path):
                        body = validator.validate(raw)
                        origin = {"kind": "import", "file": source_label(path), "sha256": before, "locator": locator}
                        try:
                            self.spool.execute("INSERT INTO entries VALUES (?, ?)", (
                                body["record_id"], canonical({"record": body, "origin": origin})
                            ))
                        except sqlite3.IntegrityError as exc:
                            raise ConflictError(f"输入存在重复 record_id：{body['record_id']}") from exc
                        count += 1
                        licenses = self.summary["license_counts"]
                        licenses[body["license_status"]] = licenses.get(body["license_status"], 0) + 1
                except (ValueError, TypeError, UnicodeError, csv.Error) as exc:
                    raise RecordError(f"{source_label(path)} ({locator}): {exc}") from exc
                if file_hash(path) != before:
                    raise ConflictError(f"扫描期间输入发生变化：{source_label(path)}")
                self.summary["files"].append({"file": source_label(path), "sha256": before, "records": count})
                self.summary["records"] += count
            if not self.summary["records"]:
                raise RecordError("输入没有记录。")
            self.spool.commit()
        except BaseException:
            self.close()
            raise

    def batches(self, size: int):
        cursor = self.spool.execute("SELECT entry FROM entries ORDER BY rowid")
        while rows := cursor.fetchmany(size):
            yield [json.loads(row[0]) for row in rows]

    def close(self):
        self.spool.close()
        self.tmp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def write_receipt(path: Path, receipt: dict):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def execute_plan(plan: Plan, store: Store, *, batch_size: int = 100, replace: bool = False) -> dict:
    if not 1 <= batch_size <= 1000:
        raise RecordError("batch_size 必须在 1–1000。")
    receipts = store.home / "receipts"
    receipts.mkdir(exist_ok=True)
    path = receipts / f"{uuid.uuid4().hex}.json"
    receipt = {"status": "RUNNING", "started_at": now(), "input": plan.summary,
               "inserted": 0, "updated": 0, "unchanged": 0, "confirmed_batches": 0,
               "policy": "metadata_only_not_curated", "replace": replace}
    write_receipt(path, receipt)
    try:
        for batch in plan.batches(batch_size):
            counts = store.import_batch(batch, replace=replace)
            for key, count in counts.items():
                receipt[key] += count
            receipt["confirmed_batches"] += 1
            write_receipt(path, receipt)
        receipt["status"] = "PASS_WITH_WARNINGS" if any(
            key != "open" and count for key, count in plan.summary["license_counts"].items()
        ) else "PASS"
    except Exception as exc:
        receipt.update(status="FAIL", error=str(exc), recovery="保留已确认批次；重跑前先恢复待处理写入日志。")
        raise
    finally:
        receipt["finished_at"] = now()
        write_receipt(path, receipt)
    return {**receipt, "receipt": str(path)}
