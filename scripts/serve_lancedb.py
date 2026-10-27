#!/usr/bin/env python3
"""Run the local CRUD service. Import data with import_lancedb.py before starting."""
from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn
from lancedb_app.records import DEFAULT_HOME
from lancedb_app.web import create_app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("端口必须在 1–65535。")
    print(f"本地管理页面：http://127.0.0.1:{args.port}；Ctrl+C 停止服务。")
    uvicorn.run(create_app(args.home), host="127.0.0.1", port=args.port, workers=1, access_log=False)


if __name__ == "__main__":
    main()
