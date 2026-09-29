#!/usr/bin/env python3
"""Run local controlled-sample reproduction, then rebuild governance reports."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "scripts/reproduce_samples.py", "--clean"],
    [sys.executable, "scripts/publish_curated_index.py"],
    [sys.executable, "scripts/validate_downloaded_artifacts.py", "--clean"],
    [sys.executable, "scripts/import_deliverables.py", "--clean"],
    [sys.executable, "scripts/build_governance.py", "--clean"],
    [sys.executable, "scripts/run_pipeline.py", "--clean", "--input-root", "datasets"],
]
for command in COMMANDS:
    print("+", " ".join(command))
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode:
        raise SystemExit(completed.returncode)
print("Controlled-sample validation and governance rebuild completed.")
