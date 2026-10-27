"""Single-writer LanceDB store with durable mutation journal and optimistic revisions.

The SQLite journal is written BEFORE LanceDB, and replayed before each operation.
This makes an interrupted write recoverable without claiming a cross-database transaction.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import lancedb
import pyarrow as pa

from .records import (
    ConflictError,
    NotFoundError,
    RecordError,
    Validator,
    canonical,
    checked_home,
    digest,
    display_fields,
    import_equivalent,
)

TABLE_NAME = "records_v1"
FIELDS = (
    "record_id", "record_type", "source_id", "license_status", "record_status", "title", "text",
    "dataset_id", "asset_uri", "search_text", "body_json", "content_sha256", "origin_json", "created_at", "updated_at",
)
SCHEMA = pa.schema([*(pa.field(name, pa.string(), nullable=False) for name in FIELDS),
                    pa.field("revision", pa.int64(), nullable=False),
                    pa.field("deleted", pa.bool_(), nullable=False),
                    pa.field("user_modified", pa.bool_(), nullable=False)])


def now() -> str:
    return datetime.now(UTC).isoformat()


def literal(value: str) -> str:
    """Quote values, never allow caller-provided SQL expressions or column names."""
    return "'" + value.replace("'", "''") + "'"


def public(row: dict) -> dict:
    return {
        "record": json.loads(row["body_json"]),
        "system": {key: row[key] for key in (
            "revision", "deleted", "user_modified", "created_at", "updated_at", "content_sha256"
        )},
        "origin": json.loads(row["origin_json"]),
        "display": {key: row[key] for key in ("title", "text")},
    }


class Store:
    def __init__(self, home: Path, validator: Validator | None = None):
        self.home = checked_home(home)
        self.home.mkdir(parents=True, exist_ok=True)
        self.validator = validator or Validator()
        self.mutex = threading.RLock()
        self.lock_file = (self.home / "writer.lock").open("a+b")
        self.journal = None
        self.db = None
        try:
            self.lock_file.seek(0, 2)
            if self.lock_file.tell() == 0:
                self.lock_file.write(b"0")
                self.lock_file.flush()
            self.lock_file.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.lock_file.close()
            raise ConflictError("数据库正被其他进程使用。请先停止 Web 服务再运行导入，或选择其他 --home。") from exc
        try:
            self.journal = sqlite3.connect(self.home / "journal.sqlite3", check_same_thread=False)
            self.journal.execute("PRAGMA synchronous=FULL")
            self.journal.execute(
                "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, action TEXT NOT NULL, "
                "at TEXT NOT NULL, rows_json TEXT NOT NULL, applied INTEGER NOT NULL DEFAULT 0)"
            )
            self.journal.commit()
            self.db = lancedb.connect(str(self.home / "database"))
            self.table = self.db.create_table(TABLE_NAME, schema=SCHEMA, exist_ok=True)
            if self.table.schema != SCHEMA:
                raise RecordError("数据库表结构与本版不一致，请使用新 --home 或显式迁移。")
            self._recover()
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.journal is not None:
            self.journal.close()
            self.journal = None
        # Local LanceDBConnection has no close() API; release table/connection references.
        self.table = None
        self.db = None
        if not self.lock_file.closed:
            # Closing the descriptor releases the operating-system lock, including after crashes.
            self.lock_file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @contextmanager
    def session(self):
        with self.mutex:
            self._recover()
            yield

    def _recover(self):
        for event_id, rows_json in self.journal.execute(
            "SELECT id, rows_json FROM events WHERE applied = 0 ORDER BY id"
        ).fetchall():
            rows = json.loads(rows_json)
            self.table.merge_insert("record_id").when_matched_update_all().when_not_matched_insert_all().execute(
                pa.Table.from_pylist(rows, schema=SCHEMA)
            )
            for row in rows:
                found = self._get(row["record_id"])
                if found != row:
                    raise RuntimeError(f"LanceDB 回读不一致：{row['record_id']}，保留待恢复日志。")
            self.journal.execute("UPDATE events SET applied = 1 WHERE id = ?", (event_id,))
            self.journal.commit()

    def _commit(self, action: str, rows: list[dict]):
        if not rows:
            return
        self.journal.execute(
            "INSERT INTO events(action, at, rows_json) VALUES (?, ?, ?)", (action, now(), canonical(rows))
        )
        self.journal.commit()
        self._recover()

    def _get(self, record_id: str) -> dict | None:
        rows = self.table.search().where(f"record_id = {literal(record_id)}").limit(2).to_list()
        if len(rows) > 1:
            raise RuntimeError(f"数据库出现重复 ID：{record_id}")
        return rows[0] if rows else None

    def get(self, record_id: str) -> dict:
        with self.session():
            row = self._get(record_id)
            if row is None:
                raise NotFoundError("记录不存在。")
            return public(row)

    def _row(self, body: dict, origin: dict, old: dict | None = None, user_modified: bool = False) -> dict:
        at = now()
        return {
            **{key: body[key] for key in ("record_id", "record_type", "source_id", "license_status", "record_status")},
            **display_fields(body), "body_json": canonical(body), "content_sha256": digest(body),
            "origin_json": canonical(origin), "created_at": old["created_at"] if old else at, "updated_at": at,
            "revision": old["revision"] + 1 if old else 1, "deleted": False, "user_modified": user_modified,
        }

    def create(self, body: object) -> dict:
        body = self.validator.validate(body)
        with self.session():
            if self._get(body["record_id"]):
                raise ConflictError("record_id 已存在，包括已撤回记录。")
            row = self._row(body, {"kind": "web"}, user_modified=True)
            self._commit("create", [row])
            return public(row)

    def update(self, record_id: str, body: object, revision: int) -> dict:
        body = self.validator.validate(body)
        if body["record_id"] != record_id:
            raise RecordError("record_id 不可修改。")
        with self.session():
            old = self._require_revision(record_id, revision)
            if old["deleted"]:
                raise ConflictError("请先恢复已撤回记录再编辑。")
            row = self._row(body, json.loads(old["origin_json"]), old, user_modified=True)
            self._commit("update", [row])
            return public(row)

    def _require_revision(self, record_id: str, revision: int) -> dict:
        old = self._get(record_id)
        if old is None:
            raise NotFoundError("记录不存在。")
        if old["revision"] != revision:
            raise ConflictError("记录已被修改，请刷新后重新操作。")
        return old

    def set_deleted(self, record_id: str, revision: int, deleted: bool) -> dict:
        with self.session():
            old = self._require_revision(record_id, revision)
            if old["deleted"] == deleted:
                raise ConflictError("记录已经处于该状态。")
            row = {**old, "revision": revision + 1, "deleted": deleted, "updated_at": now(), "user_modified": True}
            self._commit("withdraw" if deleted else "restore", [row])
            return public(row)

    def list_records(self, *, limit: int = 25, offset: int = 0, q: str = "", record_type: str = "",
                     license_status: str = "", source_id: str = "", include_deleted: bool = False) -> dict:
        if not 1 <= limit <= 100 or offset < 0:
            raise RecordError("limit 必须在 1–100，offset 不得小于 0。")
        filters = [] if include_deleted else ["deleted = false"]
        for field, value in (("record_type", record_type), ("license_status", license_status), ("source_id", source_id)):
            if value:
                filters.append(f"{field} = {literal(value)}")
        if q:
            filters.append(f"search_text LIKE {literal('%' + q.lower() + '%')}")
        where = " AND ".join(filters) or "true"
        with self.session():
            total = self.table.count_rows(where)
            rows = self.table.search().where(where).offset(offset).limit(limit).to_list()
            return {"items": [public(row) for row in rows], "total": total, "limit": limit, "offset": offset}

    def stats(self) -> dict:
        with self.session():
            return {"total": self.table.count_rows(), "active": self.table.count_rows("deleted = false"),
                    "withdrawn": self.table.count_rows("deleted = true"), "table": TABLE_NAME,
                    "vector_search": False}

    def history(self, record_id: str) -> list[dict]:
        with self.session():
            if self._get(record_id) is None:
                raise NotFoundError("记录不存在。")
            result = []
            for event_id, action, at, rows_json in self.journal.execute(
                "SELECT id, action, at, rows_json FROM events WHERE applied = 1 ORDER BY id DESC"
            ):
                for row in json.loads(rows_json):
                    if row["record_id"] == record_id:
                        result.append({"event_id": event_id, "action": action, "at": at, **public(row)})
            return result

    def import_batch(self, entries: list[dict], *, replace: bool = False) -> dict:
        """Reject duplicate IDs and conflicts for the whole batch before recording any mutation."""
        with self.session():
            rows, seen = [], set()
            counts = {"inserted": 0, "updated": 0, "unchanged": 0}
            for entry in entries:
                body = self.validator.validate(entry["record"])
                rid = body["record_id"]
                if rid in seen:
                    raise ConflictError(f"批次内 record_id 重复：{rid}")
                seen.add(rid)
                old = self._get(rid)
                if old and old["deleted"]:
                    raise ConflictError(f"{rid} 已撤回，导入不能自动恢复。")
                if old and import_equivalent(json.loads(old["body_json"]), body):
                    counts["unchanged"] += 1
                    continue
                if old and (not replace or old["user_modified"]):
                    raise ConflictError(f"{rid} 内容冲突；--replace 仅允许更新未经 Web 修改的导入记录。")
                rows.append(self._row(body, entry["origin"], old))
                counts["updated" if old else "inserted"] += 1
            self._commit("import", rows)
            return counts
