#!/usr/bin/env python3
"""Validate accepted external DroneRF RAR artifacts against receipts and controlled samples."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "downloaded" / "SRC-DRONERF-1C11757D5B"
STAGING = ROOT / "data" / "staging" / "downloaded" / "DroneRF"
CONTROLLED = ROOT / "data" / "staging" / "controlled_samples" / "DroneRF" / "data"
REPORTS = ROOT / "data" / "reports"
RESULTS = ROOT / "data" / "samples" / "download_validation_results"


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def archive_check(path: Path, member: str, target: Path) -> dict[str, object]:
    listing = run("bsdtar", "-tf", str(path))
    names = [line for line in listing.stdout.splitlines() if line]
    target.parent.mkdir(parents=True, exist_ok=True)
    extract = subprocess.run(["bsdtar", "-xOf", str(path), member], check=False, stdout=target.open("wb"), stderr=subprocess.PIPE, text=True)
    return {"archive": path.relative_to(ROOT).as_posix(), "list_exit_code": listing.returncode, "list_error": listing.stderr.strip(), "member_count": len(names), "expected_member_present": member in names, "extract_exit_code": extract.returncode, "extract_error": extract.stderr.strip(), "extracted_path": target.relative_to(ROOT).as_posix(), "extracted_sha256": sha256(target) if target.exists() else None, "extracted_size_bytes": target.stat().st_size if target.exists() else None}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate accepted DroneRF RAR files and compare segment 0 to controlled sample.")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    if shutil.which("bsdtar") is None:
        raise SystemExit("bsdtar is required to inspect RAR artifacts in this environment")
    if args.clean and STAGING.exists():
        shutil.rmtree(STAGING)
    targets = [
        (next(RAW.glob("*/RF_Data_10000_L.rar")), "RF Data_10000_L/10000L_0.csv", STAGING / "RF Data_10000_L" / "10000L_0.csv", CONTROLLED / "RF Data_10000_L" / "10000L_0.csv"),
        (next(RAW.glob("*/RF_Data_10000_H.rar")), "RF Data_10000_H/10000H_0.csv", STAGING / "RF Data_10000_H" / "10000H_0.csv", CONTROLLED / "RF Data_10000_H" / "10000H_0.csv"),
    ]
    artifacts = []
    for archive, member, extracted, controlled in targets:
        item = archive_check(archive, member, extracted)
        item["archive_sha256"] = sha256(archive)
        item["controlled_sample_path"] = controlled.relative_to(ROOT).as_posix()
        item["controlled_sample_sha256"] = sha256(controlled) if controlled.exists() else None
        item["matches_controlled_segment0"] = item["extracted_sha256"] == item["controlled_sample_sha256"]
        artifacts.append(item)
    passed = all(item["list_exit_code"] == 0 and item["expected_member_present"] and item["extract_exit_code"] == 0 and item["matches_controlled_segment0"] for item in artifacts)
    result = {"record_type": "downloaded_artifact_validation", "checked_at": now(), "dataset": "DroneRF", "scope": "official Mendeley RAR archive listing and extraction of segment 0; comparison with independently validated controlled sample", "status": "PASS" if passed else "FAIL", "artifacts": artifacts, "limitations": ["Archive listing and selected segment extraction were performed; every member was not fully decompressed.", "CSV semantic/model-label interpretation remains limited to the member-two manifest and filename convention."]}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "DroneRF_10000_LH.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Downloaded artifact validation — DroneRF 10000 L/H", "", f"- Status: **{result['status']}**", f"- Checked: `{result['checked_at']}`", "", "## Results"]
    for item in artifacts:
        lines.append(f"- `{item['archive']}`: members={item['member_count']}; selected segment extracted={item['extract_exit_code'] == 0}; SHA-256 matches controlled segment 0={item['matches_controlled_segment0']}.")
    lines += ["", "## Limits"] + [f"- {value}" for value in result["limitations"]]
    (REPORTS / "download_validation_DroneRF_10000_LH.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "artifacts": len(artifacts)}, ensure_ascii=False))
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
