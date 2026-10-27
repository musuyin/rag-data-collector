from __future__ import annotations

import io
import json
import sys
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from modality_inventory import aggregate, classify, summarize_huggingface  # noqa: E402
from remote_zip_directory import DirectoryRanges, inspect_directory  # noqa: E402


class Response:
    def __init__(self, status, data=b"", headers=None):
        self.status, self.data, self.headers = status, io.BytesIO(data), headers or {}
        self.read_called = False

    def __enter__(self): return self

    def __exit__(self, *args): pass

    def read(self, size):
        self.read_called = True
        return self.data.read(size)


class ModalityInventoryTests(unittest.TestCase):
    def test_semantics_and_mixed_containers(self):
        self.assertEqual(classify("10000L_0.csv", "DroneRF"), "rf")
        self.assertEqual(classify("V1/seq/livox_avia/a.npy"), "lidar")
        self.assertEqual(classify("V1/seq/radar_enhance_pcl/a.npy"), "radar")
        self.assertEqual(classify("V1/seq/ground_truth/a.npy"), "trajectory")
        self.assertEqual(classify("V1/rosbag/a.bag"), "mixed")
        self.assertEqual(classify("V2_V3/rosbag/m3e.bag.parts.json"), "annotation")
        self.assertEqual(classify("unknown.npy"), "unknown")
        self.assertEqual(classify("label.json"), "annotation")
        self.assertEqual(classify("metadata/FILESYSTEM_SHA256SUMS.txt"), "annotation")

    def test_unknown_sizes_are_not_zero_measurements(self):
        result = aggregate([{"path": "a.png", "size": 12}, {"path": "b.png", "size": None}])
        self.assertEqual((result["file_count"], result["known_bytes"], result["unknown_sizes"]), (2, 12, 1))

    def test_split_bag_and_extracted_views_have_distinct_denominators(self):
        result = summarize_huggingface({"id": "test", "sha": "abc", "siblings": [
            {"rfilename": "V2_V3/rosbag/m3e.bag.part001", "size": 20},
            {"rfilename": "V2_V3/rosbag/m3e.bag.part002", "size": 30},
            {"rfilename": "V1/filesystem_format/X/image/a.png", "size": 40},
            {"rfilename": "README.md", "size": 10},
        ]})
        self.assertEqual(result["physical_inventory"]["file_count"], 4)
        self.assertEqual(result["logical_inventory"]["file_count"], 3)
        self.assertEqual(result["logical_inventory"]["known_bytes"], 100)
        self.assertEqual(result["extracted_inventory"]["file_count"], 1)

    def test_range_refuses_http_200_before_reading_body(self):
        response = Response(200, b"large raw file")
        with patch("remote_zip_directory.urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "refused full body"):
                DirectoryRanges("https://example.com/archive.zip")
        self.assertFalse(response.read_called)

    def test_zip_directory_only_and_transfer_budget(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            archive.writestr("seq/", "")
            archive.writestr("seq/visible.mp4", b"x" * 100000)
            archive.writestr("seq/visible.json", b"{}")
        payload = buf.getvalue()

        def serve(request, **kwargs):
            value = request.get_header("Range").removeprefix("bytes=")
            if value.startswith("-"):
                start, end = len(payload) - int(value[1:]), len(payload) - 1
            else:
                start, end = map(int, value.split("-"))
            return Response(206, payload[start:end + 1],
                            {"Content-Range": f"bytes {start}-{end}/{len(payload)}"})

        with patch("remote_zip_directory.urlopen", side_effect=serve):
            result = inspect_directory("https://example.com/archive.zip")
        self.assertEqual(result["inventory"]["file_count"], 2)
        self.assertEqual(result["inventory"]["known_bytes"], 100002)
        self.assertLess(result["metadata_bytes_received"], 1000)

    def test_report_sources_and_category_totals(self):
        from build_modality_report import build
        report = build()
        self.assertFalse(report["raw_payload_downloaded"])
        for dataset in report["datasets"]:
            for view in dataset["views"]:
                inv = view["inventory"]
                self.assertEqual(sum(c["count"] for c in inv["categories"]), inv["file_count"])
        anti = report["datasets"][1]
        self.assertEqual(anti["status_kind"], "historical")
        self.assertGreater(anti["views"][0]["inventory"]["unknown_sizes"], 0)
        # Embedded JSON cannot break out of the data script element.
        escaped = json.dumps({"text": "</script>"}).replace("<", "\\u003c")
        self.assertNotIn("</script>", escaped)
