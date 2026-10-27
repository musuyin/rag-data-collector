"""Validate public record bodies while preserving all original domain fields."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOME = ROOT / "data" / "local" / "lancedb_manager"
MAX_RECORD_BYTES = 2 * 1024 * 1024


def checked_home(home: Path) -> Path:
    home = home.resolve()
    protected = [ROOT / name for name in (
        "datasets", "data/raw", "data/curated", "data/records", "data/normalized", "data/manifests",
        "data/reports", "configs", "schemas", "templates", "scripts", "tests", "docs", ".git", ".agents", ".codex",
    )]
    if home == ROOT or any(home.is_relative_to(path) or path.is_relative_to(home) for path in protected):
        raise RecordError("--home 不能覆盖原件、代码、配置或现有治理产物；请使用 data/local/ 下的目录。")
    return home


class RecordError(ValueError):
    status_code = 422


class ConflictError(RecordError):
    status_code = 409


class NotFoundError(RecordError):
    status_code = 404


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def import_equivalent(left: dict, right: dict) -> bool:
    """Existing member importers refresh this bookkeeping timestamp on every rebuild."""
    copies = []
    for body in (left, right):
        copy = json.loads(canonical(body))
        if copy.get("record_type") in {"model", "dataset"} and isinstance(copy.get("import_metadata"), dict):
            copy["import_metadata"].pop("imported_at", None)
        copies.append(copy)
    return copies[0] == copies[1]


class Validator:
    def __init__(self, root: Path = ROOT):
        self.sources = json.loads((root / "configs/sources/sources.json").read_text(encoding="utf-8"))
        self.source_ids = {item["source_id"] for item in self.sources}
        self.validators = {}
        for name in ("ingestion_record", "model_record", "dataset_card"):
            schema = json.loads((root / f"schemas/{name}.schema.json").read_text(encoding="utf-8"))
            self.validators[name] = Draft202012Validator(schema)

    def validate(self, body: object) -> dict:
        if not isinstance(body, dict):
            raise RecordError("每条记录必须是 JSON 对象。")
        try:
            encoded = canonical(body)
        except (ValueError, TypeError) as exc:
            raise RecordError("记录必须是合法 JSON，不能包含 NaN 或 Infinity。") from exc
        if len(encoded.encode("utf-8")) > MAX_RECORD_BYTES:
            raise RecordError("单条记录不能超过 2 MiB；请使用受控文件引用。")
        for name in ("ingestion_record", {"model": "model_record", "dataset": "dataset_card"}.get(
            body.get("record_type") if isinstance(body.get("record_type"), str) else ""
        )):
            if name:
                for error in self.validators[name].iter_errors(body):
                    field = ".".join(str(part) for part in error.absolute_path) or "record"
                    raise RecordError(f"{field}: {error.message}")
        if body["source_id"] not in self.source_ids:
            raise RecordError("source_id 未登记，请先在 configs/sources/sources.json 登记来源。")
        # This first release stores metadata, never silently treats supplied arrays as searchable vectors.
        if "vector" in body or "embedding" in body:
            raise RecordError("本版不接收 vector/embedding；请先导入元数据，向量检索后续单独接入。")
        return json.loads(encoded)


def display_fields(body: dict) -> dict:
    title = body.get("title") or body.get("dataset_name") or " ".join(
        str(body.get(key, "")) for key in ("manufacturer", "model")
    ).strip() or body["record_id"]
    text = body.get("text", "")
    if not text and body.get("record_type") == "model":
        text = "\n".join(item.get("quote", "") for item in body.get("evidence", []))
    return {
        "title": title, "text": text, "dataset_id": body.get("dataset_id", ""),
        "asset_uri": body.get("asset_uri", ""),
        "search_text": f"{body['record_id']}\n{title}\n{text}".lower(),
    }
