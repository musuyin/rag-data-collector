from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_pipeline.py"
spec = importlib.util.spec_from_file_location("run_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def test_sha256_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.txt"
            path.write_text("same input", encoding="utf-8")
            self.assertEqual(
                pipeline.sha256(path),
                "c2f991739d5824b4e1d8bafaffb735b9e4061f801d82c4aaf57aea02495f750c",
            )

    def test_exact_duplicates_are_grouped(self) -> None:
        manifest = [
            {"sha256": "a", "relative_path": "a.txt"},
            {"sha256": "b", "relative_path": "b.txt"},
            {"sha256": "a", "relative_path": "copy-a.txt"},
        ]
        groups = pipeline.duplicates(manifest)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["sha256"], "a")
        self.assertEqual(len(groups[0]["files"]), 2)

    def test_unknown_source_is_an_error(self) -> None:
        schema = json.loads((ROOT / "schemas" / "dataset_card.schema.json").read_text(encoding="utf-8"))
        record = {
            "record_id": "DATASET-X", "record_type": "dataset", "dataset_name": "X",
            "modalities": ["image"], "formats": ["jpg"], "license_status": "open",
            "source_id": "SRC-NOT-REGISTERED", "download_url": "https://example.invalid/x",
            "sample_validation_status": "pending", "record_status": "draft",
        }
        issues = pipeline.record_issues(record, schema, {"SRC-REAL"}, ROOT / "data" / "records" / "x.json")
        self.assertTrue(any(item["level"] == "ERROR" and item["field"] == "source_id" for item in issues))


if __name__ == "__main__":
    unittest.main()
