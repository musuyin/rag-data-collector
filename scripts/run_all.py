#!/usr/bin/env python3
"""Rebuild every offline artifact from the immutable member deliveries."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "scripts/import_deliverables.py", "--clean"],
    [sys.executable, "scripts/build_governance.py", "--clean"],
    [sys.executable, "scripts/run_pipeline.py", "--clean", "--input-root", "datasets"],
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
]
for command in COMMANDS:
    print("+", " ".join(command))
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode:
        raise SystemExit(completed.returncode)
print("Offline governance rebuild completed.")
