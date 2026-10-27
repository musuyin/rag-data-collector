from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from import_lancedb import main as import_main  # noqa: E402
from lancedb_app.ingestion import Plan, execute_plan  # noqa: E402
from lancedb_app.records import ConflictError, RecordError, Validator, checked_home, import_equivalent  # noqa: E402
from lancedb_app.store import Store  # noqa: E402
from lancedb_app.web import create_app  # noqa: E402


class LanceDBTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.home = self.base / "manager"
        self.validator = Validator()
        self.source_id = self.validator.sources[0]["source_id"]

    def record(self, rid="DOC-ONE", **changes):
        return {"record_id": rid, "record_type": "document", "title": "无人机资料", "text": "中文测试",
                "source_id": self.source_id, "license_status": "unknown", "record_status": "draft", **changes}

    def write_json(self, body, name="input.json"):
        path = self.base / name
        path.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
        return path

    def test_import_readback_repeat_and_input_unchanged(self):
        path = self.write_json([self.record(), self.record("DOC-TWO")])
        original = path.read_bytes()
        with Plan([path], self.validator) as plan, Store(self.home) as store:
            first = execute_plan(plan, store, batch_size=1)
            second = execute_plan(plan, store)
            self.assertEqual(first["inserted"], 2)
            self.assertEqual(first["status"], "PASS_WITH_WARNINGS")
            self.assertEqual(second["unchanged"], 2)
            self.assertEqual(store.stats()["total"], 2)
            self.assertEqual(store.get("DOC-ONE")["origin"]["locator"], "json:1")
            self.assertEqual(store.get("DOC-ONE")["record"], self.record())
            self.assertEqual(store.get("DOC-ONE")["system"]["revision"], 1)
        self.assertEqual(original, path.read_bytes())

    def test_bad_input_and_duplicate_ids_never_create_database(self):
        for data in ([self.record(), self.record(source_id="UNREGISTERED")], [self.record(), self.record()]):
            path = self.write_json(data)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(import_main(["--input", str(path), "--home", str(self.home)]), 1)
            self.assertFalse(self.home.exists())

    def test_dry_run_is_read_only_and_csv_jsonl_work(self):
        path = self.write_json(self.record())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(import_main(["--input", str(path), "--home", str(self.home), "--dry-run"]), 0)
        self.assertFalse(self.home.exists())
        jsonl = self.base / "records.jsonl"
        jsonl.write_text("\ufeff" + json.dumps(self.record(), ensure_ascii=False) + "\n\n", encoding="utf-8")
        csv_path = self.base / "records.csv"
        csv_path.write_text(
            "record_id,record_type,title,source_id,license_status,record_status\n"
            f"DOC-CSV,document,测试,{self.source_id},unknown,draft\n", encoding="utf-8-sig"
        )
        with Plan([jsonl, csv_path], self.validator) as plan:
            self.assertEqual(plan.summary["records"], 2)

    def test_model_evidence_and_vector_constraints(self):
        invalid = self.record(record_type="model", manufacturer="X", model="X", evidence=[])
        for body in (invalid, self.record(vector=[1, 2]), self.record(text=float("nan")), {"record_id": "ONLY"}):
            with self.assertRaises(RecordError):
                self.validator.validate(body)

    def test_crud_revisions_withdraw_restore_and_history_survive_restart(self):
        with Store(self.home) as store:
            store.create(self.record())
            updated = store.update("DOC-ONE", self.record(text="已修订"), 1)
            self.assertEqual(updated["system"]["revision"], 2)
            with self.assertRaises(ConflictError):
                store.update("DOC-ONE", self.record(), 1)
            store.set_deleted("DOC-ONE", 2, True)
            self.assertEqual(store.list_records()["total"], 0)
            self.assertEqual(store.list_records(include_deleted=True)["total"], 1)
            store.set_deleted("DOC-ONE", 3, False)
        with Store(self.home) as store:
            self.assertEqual(store.get("DOC-ONE")["record"]["text"], "已修订")
            self.assertEqual(len(store.history("DOC-ONE")), 4)

    def test_import_conflicts_protect_manual_edits_and_withdrawals(self):
        with Store(self.home) as store:
            entry = {"record": self.record(), "origin": {"kind": "test"}}
            store.import_batch([entry])
            changed = {**entry, "record": self.record(text="上游新版本")}
            with self.assertRaises(ConflictError):
                store.import_batch([changed])
            self.assertEqual(store.import_batch([changed], replace=True)["updated"], 1)
            store.update("DOC-ONE", self.record(text="人工修订"), 2)
            with self.assertRaises(ConflictError):
                store.import_batch([changed], replace=True)
            store.set_deleted("DOC-ONE", 3, True)
            with self.assertRaises(ConflictError):
                store.import_batch([changed], replace=True)

    def test_pending_journal_recovers_interrupted_lance_write(self):
        with Store(self.home) as store:
            with patch.object(store.table, "merge_insert", side_effect=RuntimeError("simulated interruption")):
                with self.assertRaises(RuntimeError):
                    store.create(self.record())
        with Store(self.home) as store:
            self.assertEqual(store.get("DOC-ONE")["system"]["revision"], 1)
            self.assertEqual(len(store.history("DOC-ONE")), 1)
            self.assertEqual(store.stats()["total"], 1)

    def test_failed_import_receipt_keeps_confirmed_batches(self):
        path = self.write_json([self.record("DOC-NEW"), self.record()])
        with Plan([path], self.validator) as plan, Store(self.home) as store:
            store.create(self.record(text="人工记录"))
            with self.assertRaises(ConflictError):
                execute_plan(plan, store, batch_size=1)
            receipt = json.loads(next((self.home / "receipts").glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], "FAIL")
            self.assertEqual(receipt["confirmed_batches"], 1)
            self.assertEqual(store.stats()["total"], 2)

    def test_process_lock_and_protected_paths(self):
        with Store(self.home):
            with self.assertRaises(ConflictError):
                Store(self.home)
        for path in (ROOT, ROOT / "datasets/db", ROOT / "data/raw/db", ROOT / "schemas/db"):
            with self.assertRaises(RecordError):
                checked_home(path)

    def test_filters_pagination_and_quoted_input(self):
        with Store(self.home) as store:
            store.create(self.record(title="O'Brien 中文"))
            store.create(self.record("DOC-TWO", license_status="restricted"))
            self.assertEqual(store.list_records(limit=1)["total"], 2)
            self.assertEqual(len(store.list_records(limit=1, offset=1)["items"]), 1)
            self.assertEqual(store.list_records(q="O'Brien")["total"], 1)
            self.assertEqual(store.list_records(q="' OR true --")["total"], 0)
            self.assertEqual(store.list_records(record_type="' OR true --")["total"], 0)
            self.assertEqual(store.list_records(license_status="restricted")["total"], 1)

    def test_existing_seven_domain_records(self):
        paths = [ROOT / "data/records/imported/models", ROOT / "data/records/imported/datasets"]
        with Plan(paths, self.validator) as plan, Store(self.home) as store:
            receipt = execute_plan(plan, store)
            self.assertEqual(receipt["inserted"], 7)
            self.assertEqual(store.list_records(record_type="model")["total"], 4)
            self.assertEqual(store.list_records(record_type="dataset")["total"], 3)

    def test_member_rebuild_timestamp_does_not_create_false_conflict(self):
        original = json.loads((ROOT / "data/records/imported/models/MODEL-SKYDIO-X10.json").read_text(encoding="utf-8"))
        changed = json.loads(json.dumps(original))
        changed["import_metadata"]["imported_at"] = "2099-01-01T00:00:00Z"
        self.assertTrue(import_equivalent(original, changed))
        with Store(self.home) as store:
            store.import_batch([{"record": original, "origin": {"kind": "test"}}])
            self.assertEqual(store.import_batch([{"record": changed, "origin": {"kind": "test"}}])["unchanged"], 1)
            self.assertEqual(store.get(original["record_id"])["record"], original)
        changed["model"] = "different"
        self.assertFalse(import_equivalent(original, changed))

    def test_web_api_security_validation_and_crud(self):
        with TestClient(create_app(self.home), base_url="http://127.0.0.1") as client:
            self.assertEqual(client.get("/").status_code, 200)
            self.assertEqual(client.get("/static/app.js").status_code, 200)
            self.assertEqual(client.get("/api/stats").json()["total"], 0)
            self.assertEqual(client.post("/api/records", json=self.record()).status_code, 403)
            self.assertEqual(client.get("/api/stats", headers={"host": "evil.example"}).status_code, 400)
            token = client.get("/api/session").json()["write_token"]
            headers = {"x-write-token": token}
            created = client.post("/api/records", json=self.record(), headers=headers)
            self.assertEqual(created.status_code, 201, created.text)
            self.assertEqual(client.post("/api/records", json=self.record(), headers=headers).status_code, 409)
            self.assertEqual(client.post("/api/records", json={"record_id": "BAD"}, headers=headers).status_code, 422)
            update = {"record": self.record(text="通过 API 修改"), "revision": 1}
            self.assertEqual(client.put("/api/records/DOC-ONE", json=update, headers=headers).status_code, 200)
            self.assertEqual(client.put("/api/records/DOC-ONE", json=update, headers=headers).status_code, 409)
            self.assertEqual(client.request("DELETE", "/api/records/DOC-ONE", headers=headers,
                                            json={"revision": 2}).status_code, 200)
            self.assertEqual(client.get("/api/records").json()["total"], 0)
            self.assertEqual(client.post("/api/records/DOC-ONE/restore", json={"revision": 3}, headers=headers).status_code, 200)
            self.assertEqual(len(client.get("/api/records/DOC-ONE/history").json()["items"]), 4)
            self.assertEqual(client.get("/api/records/NO-SUCH-ID").status_code, 404)
            self.assertEqual(client.get("/api/records?limit=0").status_code, 422)
            self.assertEqual(client.get("/api/records?q=%E4%BF%AE%E6%94%B9").json()["total"], 1)


if __name__ == "__main__":
    unittest.main()
