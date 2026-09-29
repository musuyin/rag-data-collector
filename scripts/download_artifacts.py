#!/usr/bin/env python3
"""Download explicitly approved artifacts into immutable raw storage with receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import ssl
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:
    certifi = None

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "configs" / "download_targets.json"
RAW = ROOT / "data" / "raw" / "downloaded"
RECEIPTS = ROOT / "data" / "receipts" / "downloads"
USER_AGENT = "drone-data-collector/0.1 (+research data governance; contact project owner)"


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def safe_name(value: str) -> str:
    return "".join(c if c.isalnum() or c in ".-_" else "_" for c in value).strip("._") or "artifact"


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download reviewed public artifacts only when target and CLI both allow it.")
    parser.add_argument("--target", action="append", required=True, help="Approved target_id; repeatable.")
    parser.add_argument("--allow-download", action="store_true", help="Required second confirmation.")
    args = parser.parse_args()
    if not args.allow_download:
        parser.error("--allow-download is required; no artifact is downloaded by default")
    targets = json.loads(TARGETS.read_text(encoding="utf-8")) if TARGETS.exists() else []
    by_id = {item["target_id"]: item for item in targets}
    results = []
    context = ssl.create_default_context(cafile=certifi.where()) if certifi else None
    for target_id in args.target:
        target = by_id.get(target_id)
        if not target:
            results.append({"target_id": target_id, "status": "skipped", "reason": "unknown target"}); continue
        if not target.get("approved") or not target.get("allow_download"):
            results.append({"target_id": target_id, "status": "skipped", "reason": "target must set approved=true and allow_download=true"}); continue
        url = target.get("url")
        if not url or not url.startswith("https://"):
            results.append({"target_id": target_id, "status": "skipped", "reason": "only explicit HTTPS URLs are supported"}); continue
        if target.get("expected_sha256") is None:
            results.append({"target_id": target_id, "status": "skipped", "reason": "expected_sha256 is required for immutable acceptance"}); continue
        max_bytes = int(target.get("max_bytes", 0))
        if max_bytes <= 0:
            results.append({"target_id": target_id, "status": "skipped", "reason": "positive max_bytes is required"}); continue
        receipt = {"target_id": target_id, "url": url, "started_at": now(), "status": "failed"}
        temporary = RAW / ".partial" / f"{uuid.uuid4().hex}.part"
        try:
            temporary.parent.mkdir(parents=True, exist_ok=True)
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urlopen(request, timeout=60, context=context) as response, temporary.open("wb") as output:
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > max_bytes:
                    raise ValueError(f"declared Content-Length {content_length} exceeds max_bytes {max_bytes}")
                received = 0
                while chunk := response.read(1024 * 1024):
                    received += len(chunk)
                    if received > max_bytes:
                        raise ValueError(f"download exceeded max_bytes {max_bytes}")
                    output.write(chunk)
                receipt.update({"http_status": response.status, "content_type": response.headers.get("Content-Type"), "content_length": content_length, "received_bytes": received})
            actual_sha = digest(temporary)
            if actual_sha != target["expected_sha256"]:
                raise ValueError(f"sha256 mismatch: expected {target['expected_sha256']}, got {actual_sha}")
            filename = safe_name(target.get("filename") or Path(urlparse(url).path).name)
            output = RAW / safe_name(target.get("source_id", "unknown-source")) / actual_sha[:16] / filename
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists() and digest(output) != actual_sha:
                raise ValueError(f"refusing to overwrite different immutable file: {output}")
            shutil.move(str(temporary), output)
            receipt.update({"status": "accepted", "finished_at": now(), "sha256": actual_sha, "raw_path": output.relative_to(ROOT).as_posix(), "license_status": target.get("license_status", "unknown")})
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            temporary.unlink(missing_ok=True)
            receipt.update({"finished_at": now(), "error": str(exc)})
        save_json(RECEIPTS / f"{target_id}__{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.json", receipt)
        results.append({"target_id": target_id, "status": receipt["status"], "receipt": receipt})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(row["status"] == "failed" for row in results) else 0

if __name__ == "__main__":
    sys.exit(main())
