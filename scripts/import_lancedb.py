#!/usr/bin/env python3
"""Import validated metadata into a local LanceDB. Inputs are always read-only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lancedb_app.ingestion import Plan, execute_plan
from lancedb_app.records import DEFAULT_HOME, ROOT, RecordError, Validator
from lancedb_app.store import Store


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", type=Path, help="JSON/JSONL/CSV 文件或目录；默认现有型号与数据集记录")
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME, help="数据库、操作日志与收据目录")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true", help="只校验输入，不创建数据库，不检查既有库冲突")
    parser.add_argument("--replace", action="store_true", help="允许更新内容变化的导入记录；不覆盖 Web 人工修改")
    args = parser.parse_args(argv)
    if not 1 <= args.batch_size <= 1000:
        parser.error("--batch-size 必须在 1–1000。")
    paths = args.input or [ROOT / "data/records/imported/models", ROOT / "data/records/imported/datasets"]
    try:
        validator = Validator()
        with Plan(paths, validator) as plan:
            if args.dry_run:
                result = {"status": "VALID_INPUT_ONLY", **plan.summary,
                          "note": "未检查既有数据库冲突；许可风险不会因格式校验通过而消失。"}
            else:
                with Store(args.home, validator) as store:
                    result = execute_plan(plan, store, batch_size=args.batch_size, replace=args.replace)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (RecordError, OSError, ValueError, RuntimeError) as exc:
        print(f"导入失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
