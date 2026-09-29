#!/usr/bin/env python3
"""Publish a metadata-only curated index for successfully validated controlled samples.

Controlled payloads remain under datasets/ (delivery original) and data/staging/
(regenerated inspection output). This script never copies restricted raw media into
curated/; it publishes only a traceable index and acceptance decision.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data" / "samples" / "reproduction_results"
CURATED = ROOT / "data" / "curated" / "controlled_samples"


def main() -> int:
    entries = []
    for path in sorted(RESULTS.glob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        accepted = item["status"] in {"PASS", "PASS_WITH_WARNING"}
        entries.append({
            "dataset": item["dataset"],
            "acceptance_status": "ACCEPTED_FOR_CONTROLLED_INTERNAL_USE" if accepted else "REJECTED",
            "reproduction_status": item["status"],
            "package_sha256": item["package"]["actual_sha256"],
            "package_source_path": item["package"]["source_path"],
            "reproduction_result": path.relative_to(ROOT).as_posix(),
            "content_checks": item["content_checks"],
            "license_or_internal_storage": item["upstream_manifest"]["license_or_internal_storage"],
            "payload_policy": "Payload remains in controlled delivery/staging; curated index contains no raw payload.",
        })
    output = {"generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "record_type": "curated_controlled_sample_index", "entries": entries}
    CURATED.mkdir(parents=True, exist_ok=True)
    (CURATED / "index.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"entries": len(entries), "accepted": sum(x["acceptance_status"].startswith("ACCEPTED") for x in entries)}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
