#!/usr/bin/env python3
"""Configuration-driven, terms-respecting source metadata collection.

Adapters use official/public APIs where available. A conditional request (ETag or
Last-Modified) avoids re-downloading unchanged artifacts. Downloads are opt-in.
No authentication bypassing, CAPTCHA handling, form submission, or robots bypass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import ssl
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:  # standard library fallback if certifi is unavailable
    certifi = None

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "configs" / "collection_targets.json"
STATE_FILE = ROOT / "data" / "collection_state.json"
METADATA_DIR = ROOT / "data" / "collection_metadata"
RAW_DIR = ROOT / "data" / "raw" / "collected"
USER_AGENT = "drone-data-collector/0.1 (+research data governance; contact project owner)"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_load(path: Path, default: Any) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._") or "artifact"


def request(url: str, state: dict[str, Any] | None = None) -> tuple[int, dict[str, str], bytes]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json, text/html, application/pdf, */*;q=0.2"}
    if state:
        if state.get("etag"): headers["If-None-Match"] = state["etag"]
        if state.get("last_modified"): headers["If-Modified-Since"] = state["last_modified"]
    # Some managed Python installations lack a configured CA bundle. certifi supplies
    # a standard public trust store; certificate verification remains enabled.
    context = ssl.create_default_context(cafile=certifi.where()) if certifi else None
    try:
        with urlopen(Request(url, headers=headers), timeout=30, context=context) as response:
            return response.status, dict(response.headers.items()), response.read()
    except HTTPError as error:
        if error.code == 304: return 304, dict(error.headers.items()), b""
        raise


def github(target: dict[str, Any], prior: dict[str, Any] | None) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    repository = target["repository"]
    repo_url = f"https://api.github.com/repos/{quote(repository, safe='/')}"
    status, headers, body = request(repo_url, prior)
    if status == 304: return "unchanged", {}, []
    repo = json.loads(body)
    _, _, release_body = request(repo_url + "/releases")
    releases = json.loads(release_body)
    return "updated", {"repository": repository, "api_url": repo_url, "default_branch": repo.get("default_branch"), "pushed_at": repo.get("pushed_at"), "updated_at": repo.get("updated_at"), "license": (repo.get("license") or {}).get("spdx_id"), "releases": [{"tag_name": item.get("tag_name"), "published_at": item.get("published_at"), "assets": [{"name": asset.get("name"), "url": asset.get("browser_download_url"), "size": asset.get("size")} for asset in item.get("assets", [])]} for item in releases]}, [{"url": repo_url, "headers": headers}]


def zenodo(target: dict[str, Any], prior: dict[str, Any] | None) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    url = f"https://zenodo.org/api/records/{target['record_id']}"
    status, headers, body = request(url, prior)
    if status == 304: return "unchanged", {}, []
    record = json.loads(body)
    return "updated", {"record_id": str(target["record_id"]), "api_url": url, "doi": record.get("doi"), "title": record.get("metadata", {}).get("title"), "updated": record.get("updated"), "files": [{"name": item.get("key"), "size": item.get("size"), "checksum": item.get("checksum"), "url": item.get("links", {}).get("self")} for item in record.get("files", [])]}, [{"url": url, "headers": headers}]


def mendeley(target: dict[str, Any], prior: dict[str, Any] | None) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    dataset_id, version = target["dataset_id"], target.get("version", 1)
    # Mendeley Data's public API exposes the current public version at the dataset
    # endpoint. The requested version remains recorded for audit but is not inferred
    # from an undocumented version-specific endpoint.
    url = f"https://data.mendeley.com/public-api/datasets/{quote(dataset_id)}"
    status, headers, body = request(url, prior)
    if status == 304: return "unchanged", {}, []
    record = json.loads(body)
    files = record.get("files") or record.get("data", {}).get("files", [])
    return "updated", {"dataset_id": dataset_id, "version_requested": version, "version_returned": record.get("version"), "api_url": url, "title": record.get("name") or record.get("title"), "doi": record.get("doi"), "license": record.get("data_licence") or record.get("license"), "modified_on": record.get("modified_on"), "files": [{"name": item.get("filename") or item.get("name"), "size": (item.get("content_details") or {}).get("size") or item.get("size"), "sha256": (item.get("content_details") or {}).get("sha256_hash"), "download_url": (item.get("content_details") or {}).get("download_url") or item.get("download_url") or item.get("url")} for item in files]}, [{"url": url, "headers": headers}]


def http_snapshot(target: dict[str, Any], prior: dict[str, Any] | None) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    status, headers, body = request(target["url"], prior)
    if status == 304: return "unchanged", {}, []
    return "updated", {"url": target["url"], "http_status": status, "content_type": headers.get("Content-Type", ""), "content_length": headers.get("Content-Length", ""), "body_sha256": hashlib.sha256(body).hexdigest()}, [{"url": target["url"], "headers": headers, "body": body}]


def choose_adapter(target: dict[str, Any], prior: dict[str, Any] | None):
    adapter = target["adapter"]
    if adapter == "github_repo": return github(target, prior)
    if adapter == "zenodo_record": return zenodo(target, prior)
    if adapter == "mendeley_dataset": return mendeley(target, prior)
    if adapter in {"http", "regulatory_snapshot"}: return http_snapshot(target, prior)
    raise ValueError(f"unsupported adapter: {adapter}")


def store_artifact(target: dict[str, Any], responses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not target.get("allow_download"):
        return []
    saved = []
    for response in responses:
        body = response.get("body")
        if body is None: continue
        content_type = response["headers"].get("Content-Type", "").split(";", 1)[0]
        extension = mimetypes.guess_extension(content_type) or Path(response["url"].split("?", 1)[0]).suffix or ".bin"
        filename = f"{safe_name(target['target_id'])}__{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}__{safe_name(Path(response['url'].split('?', 1)[0]).name) or 'snapshot'}{extension if not str(response['url']).endswith(extension) else ''}"
        output = RAW_DIR / filename
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(body)
        saved.append({"path": output.relative_to(ROOT).as_posix(), "sha256": digest_file(output), "size_bytes": output.stat().st_size, "url": response["url"]})
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect approved public source metadata with conditional updates.")
    parser.add_argument("--target", action="append", help="Target ID to run; repeatable. Default: all enabled targets.")
    parser.add_argument("--dry-run", action="store_true", help="Show selected targets without network access or state changes.")
    parser.add_argument("--allow-download", action="store_true", help="Permit artifact download only for targets with allow_download=true.")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds to wait between targets (default: 1).")
    args = parser.parse_args()
    targets = json_load(TARGETS, [])
    selected = [item for item in targets if (not args.target and item.get("enabled")) or (args.target and item["target_id"] in args.target)]
    if not selected:
        print("No targets selected. Enable a reviewed target or pass --target TARGET_ID.")
        return 0
    if args.dry_run:
        for item in selected: print(json.dumps({key: item.get(key) for key in ("target_id", "source_id", "adapter", "enabled", "allow_download", "url", "repository", "dataset_id", "record_id") if item.get(key) not in (None, "")}))
        return 0
    state = json_load(STATE_FILE, {})
    results = []
    for index, target in enumerate(selected):
        if target.get("source_id") == "SRC-TO-BE-REGISTERED":
            results.append({"target_id": target["target_id"], "status": "skipped", "reason": "source_id must be registered first"}); continue
        if target["adapter"] == "regulatory_snapshot" and not target.get("url"):
            results.append({"target_id": target["target_id"], "status": "skipped", "reason": "official result URL requires human approval"}); continue
        try:
            prior = state.get(target["target_id"])
            status, metadata, responses = choose_adapter(target, prior)
            metadata_sha256 = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest() if metadata else (prior or {}).get("metadata_sha256", "")
            # Some public APIs do not emit validators. In that case the normalized
            # metadata digest provides a deterministic fallback for incrementality.
            if status == "updated" and prior and metadata_sha256 == prior.get("metadata_sha256"):
                status = "unchanged"
            artifact_target = dict(target)
            artifact_target["allow_download"] = bool(target.get("allow_download") and args.allow_download and status == "updated")
            artifacts = store_artifact(artifact_target, responses)
            headers = responses[0]["headers"] if responses else (prior or {})
            state[target["target_id"]] = {"target_id": target["target_id"], "source_id": target["source_id"], "adapter": target["adapter"], "checked_at": utc_now(), "etag": headers.get("ETag") or (prior or {}).get("etag"), "last_modified": headers.get("Last-Modified") or (prior or {}).get("last_modified"), "metadata_sha256": metadata_sha256, "artifacts": artifacts}
            if status == "updated": json_write(METADATA_DIR / f"{safe_name(target['target_id'])}.json", {"collected_at": utc_now(), "target": target, "metadata": metadata})
            results.append({"target_id": target["target_id"], "status": status, "artifacts": artifacts})
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            results.append({"target_id": target["target_id"], "status": "failed", "error": str(exc)})
        if index < len(selected) - 1: time.sleep(max(args.pause, 0))
    json_write(STATE_FILE, state)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(item["status"] == "failed" for item in results) else 0

if __name__ == "__main__":
    sys.exit(main())
