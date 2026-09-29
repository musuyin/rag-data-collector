#!/usr/bin/env python3
"""Independently validate member-two controlled sample packages without modifying datasets/."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import struct
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "datasets" / "member2_controlled_samples"
PACKAGES = DELIVERY / "packages"
STAGING = ROOT / "data" / "staging" / "controlled_samples"
RESULTS = ROOT / "data" / "samples" / "reproduction_results"
REPORTS = ROOT / "data" / "reports"


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_extract(archive: Path, output: Path) -> list[str]:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            destination = (output / member.filename).resolve()
            if not destination.is_relative_to(output.resolve()):
                raise ValueError(f"unsafe archive path: {member.filename}")
        package.extractall(output)
        return [member.filename for member in package.infolist() if not member.is_dir()]


def png_info(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        signature = handle.read(26)
    if signature[:8] != b"\x89PNG\r\n\x1a\n" or signature[12:16] != b"IHDR":
        raise ValueError("invalid PNG signature/IHDR")
    width, height, bit_depth, color_type = struct.unpack(">IIBB", signature[16:26])
    return {"format": "png", "width": width, "height": height, "bit_depth": bit_depth, "color_type": color_type}


def npy_info(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        magic = handle.read(6)
        if magic != b"\x93NUMPY":
            raise ValueError("invalid NPY magic")
        major, minor = struct.unpack("BB", handle.read(2))
        length_size = 2 if major == 1 else 4
        header_length = int.from_bytes(handle.read(length_size), "little")
        header = handle.read(header_length).decode("latin1")
    return {"format": "npy", "version": f"{major}.{minor}", "header": header.strip()}


def mp4_info(path: Path) -> dict[str, Any]:
    # Structural check only: ffprobe/OpenCV are deliberately not required.
    with path.open("rb") as handle:
        prefix = handle.read(64)
    if b"ftyp" not in prefix:
        raise ValueError("missing ISO BMFF ftyp box")
    return {"format": "mp4", "bytes": path.stat().st_size, "ftyp_present": True, "deep_decode": "NOT_PERFORMED_NO_OPTIONAL_MEDIA_TOOL"}


def csv_info(path: Path) -> dict[str, Any]:
    # DroneRF files are numeric matrices without a header. Count physical rows,
    # not an assumed header/data split, and retain only a bounded numeric preview.
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        first = next(reader, [])
        rows = 1 + sum(1 for _ in reader) if first else 0
    numeric_preview = all(_is_number(value) for value in first[: min(32, len(first))])
    return {"format": "csv", "physical_rows": rows, "columns": len(first), "header_present": not numeric_preview, "first_values": first[:8]}


def _is_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def inspect_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    result = {"path": path.as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256(path), "suffix": suffix}
    if suffix == ".png": result.update(png_info(path))
    elif suffix == ".npy": result.update(npy_info(path))
    elif suffix == ".mp4": result.update(mp4_info(path))
    elif suffix == ".csv": result.update(csv_info(path))
    elif suffix == ".json": result["json_type"] = type(load_json(path)).__name__
    return result


def check_dataset(dataset: str, root: Path) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    files = [p for p in root.rglob("*") if p.is_file() and p.name not in {"README.md", "sample_manifest.json"}]
    inspected, errors = [], []
    for path in files:
        try:
            inspected.append(inspect_file(path))
        except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError, StopIteration) as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
    rel_names = {p.relative_to(root).as_posix() for p in files}
    checks: dict[str, Any] = {}
    if dataset == "Anti-UAV300":
        required = {"data/val/20190926_200510_1_8/visible.mp4", "data/val/20190926_200510_1_8/infrared.mp4", "data/val/20190926_200510_1_8/visible.json", "data/val/20190926_200510_1_8/infrared.json"}
        checks["required_files_present"] = required <= rel_names
        annotations = [load_json(root / name) for name in sorted(required) if name.endswith(".json") and (root / name).exists()]
        checks["annotation_json_parseable"] = len(annotations) == 2
        checks["annotation_frame_counts"] = [len(value.get("exist", [])) for value in annotations]
        checks["annotation_frame_counts_match"] = len(checks["annotation_frame_counts"]) == 2 and len(set(checks["annotation_frame_counts"])) == 1
        checks["frame_pairing_basis"] = "same controlled sequence directory and equal annotation frame counts; hardware synchronization not inferred from container metadata"
    elif dataset == "DroneRF":
        l_file, h_file = "data/RF Data_10000_L/10000L_0.csv", "data/RF Data_10000_H/10000H_0.csv"
        checks["l_h_files_present"] = {l_file, h_file} <= rel_names
        csv_inspections = {p.name: inspect_file(p) for p in (root / l_file, root / h_file)}
        checks["csv_physical_rows"] = {name: item["physical_rows"] for name, item in csv_inspections.items()}
        checks["csv_columns"] = {name: item["columns"] for name, item in csv_inspections.items()}
        checks["csv_header_present"] = {name: item["header_present"] for name, item in csv_inspections.items()}
        checks["csv_numeric_preview"] = {name: item["first_values"] for name, item in csv_inspections.items()}
        checks["filename_association"] = "BUI 10000 / segment 0 / L-H pair as supplied in member-two manifest"
    elif dataset == "MMAUD":
        modalities = {"Image": ".png", "lidar_360": ".npy", "livox_avia": ".npy", "radar_enhance_pcl": ".npy"}
        timestamps = {}
        for modality, suffix in modalities.items():
            matches = list((root / "data" / "val" / "seq0001" / modality).glob(f"*{suffix}"))
            if matches:
                timestamps[modality] = float(matches[0].stem)
        checks["modalities_present"] = sorted(timestamps)
        checks["timestamp_deltas_ms_from_camera"] = {name: round(abs(value - timestamps.get("Image", value)) * 1000, 3) for name, value in timestamps.items() if name != "Image"}
        checks["association_basis"] = "seq0001 plus nearest filename timestamp; no calibration or hardware synchronization claim"
    return inspected, errors, checks


def markdown(result: dict[str, Any]) -> str:
    lines = [f"# Controlled sample reproduction — {result['dataset']}", "", f"- Checked at: `{result['checked_at']}`", f"- Result: **{result['status']}**", f"- Package: `{result['package']['source_path']}`", f"- Package SHA-256: `{result['package']['actual_sha256']}`", "", "## Package checks"]
    for key in ("size_matches_manifest", "sha256_matches_manifest", "zip_integrity", "manifest_consistency"):
        lines.append(f"- {key}: `{result['package'][key]}`")
    lines += ["", "## Content checks", "```json", json.dumps(result["content_checks"], ensure_ascii=False, indent=2), "```", "", "## Boundaries"]
    lines += ["- The source package in `datasets/` was not modified; extraction is regenerated in `data/staging/`.", "- MP4 validation is structural in this environment (no ffprobe/OpenCV installed); it is not a full frame decode.", "- Dataset-level claims are limited to this controlled sample and its declared association rule."]
    if result["errors"]:
        lines += ["", "## Errors"] + [f"- {value}" for value in result["errors"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate controlled small sample ZIPs supplied by member two.")
    parser.add_argument("--dataset", action="append", choices=["Anti-UAV300", "DroneRF", "MMAUD"], help="Repeatable; default validates all samples.")
    parser.add_argument("--clean", action="store_true", help="Regenerate staging extraction and result artifacts.")
    args = parser.parse_args()
    manifest = {item["dataset"]: item for item in load_json(DELIVERY / "sample_manifest.json")}
    delivery_summary = {item["dataset"]: item for item in load_json(DELIVERY / "delivery_summary.json")["packages"]}
    expected_hashes = {line.split()[1].split("\\")[-1]: line.split()[0] for line in (DELIVERY / "SHA256.txt").read_text(encoding="utf-8-sig").splitlines() if line.strip()}
    selected = args.dataset or sorted(manifest)
    output = []
    for dataset in selected:
        item = manifest[dataset]; package = PACKAGES / item["package_filename"]
        actual_hash, actual_size = sha256(package), package.stat().st_size
        stage = STAGING / dataset
        try:
            names = safe_extract(package, stage)
            with zipfile.ZipFile(package) as zf:
                bad_member = zf.testzip()
            zip_integrity = bad_member is None
            inspected, errors, checks = check_dataset(dataset, stage)
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            names, zip_integrity, inspected, errors, checks = [], False, [], [str(exc)], {}
        summary = delivery_summary.get(dataset, {})
        summary_conflict = bool(summary) and (summary.get("expected_size_bytes") != item["expected_size_bytes"] or summary.get("sha256") != item["sha256"])
        package_result = {"source_path": package.relative_to(ROOT).as_posix(), "actual_size_bytes": actual_size, "actual_sha256": actual_hash, "manifest_expected_size_bytes": item["expected_size_bytes"], "manifest_expected_sha256": item["sha256"], "size_matches_manifest": actual_size == item["expected_size_bytes"], "sha256_matches_manifest": actual_hash == item["sha256"], "sha256_matches_SHA256_txt": actual_hash == expected_hashes.get(package.name), "zip_integrity": zip_integrity, "archive_member_count": len(names), "manifest_consistency": "CONFLICT" if summary_conflict else "CONSISTENT", "delivery_summary_value": {"size": summary.get("expected_size_bytes"), "sha256": summary.get("sha256")} if summary else None}
        passed = all([package_result["size_matches_manifest"], package_result["sha256_matches_manifest"], package_result["sha256_matches_SHA256_txt"], zip_integrity, not errors])
        status = "PASS_WITH_WARNING" if passed and summary_conflict else ("PASS" if passed else "FAIL")
        result = {"record_type": "controlled_sample_reproduction", "dataset": dataset, "checked_at": now(), "status": status, "scope": "independent local validation of supplied controlled sample package", "package": package_result, "content_checks": checks, "inspected_files": inspected, "errors": errors, "upstream_manifest": item}
        write_json(RESULTS / f"{dataset}.json", result)
        (REPORTS / f"reproduction_{dataset}.md").write_text(markdown(result), encoding="utf-8")
        output.append({"dataset": dataset, "status": status, "errors": len(errors)})
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if any(row["status"] == "FAIL" for row in output) else 0

if __name__ == "__main__":
    sys.exit(main())
