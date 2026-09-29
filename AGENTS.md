# AGENTS.md — data-collector 协作规则

## 项目目标

本仓库是无人机型号资料、多模态数据集及其证据链的数据工程底座。重点是**可追溯、可复现、许可可见**，而非规避网站限制或自动化抓取一切内容。

## 数据分层与写入规则

- `datasets/`：成员一、二的原始交付目录，**只读**。导入脚本不得修改其中任何文件。
- `data/raw/`：将来取得的原始下载文件，只增不改；不得由去重程序自动删除。
- `data/staging/`：可再生成的解压、转换和待核验文件。
- `data/records/imported/`：从成员交付自动生成的标准化互操作记录。
- `data/normalized/`：证据 JSONL、进度和治理汇总等机器生成中间产物。
- `data/manifests/`、`data/reports/`：可再生成的哈希、重复检测与质量报告。
- `data/curated/`：仅接收质量门禁无 ERROR 的人工确认数据。

不提交大体积、受限许可或不可再分发的完整原始数据集。用受控存储位置、来源 URL、版本、哈希和访问说明替代。

## Python 环境与依赖

- 依赖唯一声明文件是 `pyproject.toml`；使用 `uv.lock` 锁定精确版本。不要新建或维护 `requirements.txt`。
- Python 基线为 3.12。首次进入项目运行 `uv sync --all-groups`，它会创建本地 `.venv/`。
- 常规命令用 `uv run python ...` 执行，避免误用全局解释器；`.venv/` 和 `.uv-cache/` 不提交，`uv.lock` 必须提交。
- 新增第三方库前优先评估能否用标准库实现；确有必要时执行 `uv add <package>`（开发工具用 `uv add --dev <package>`），并更新文档和锁文件。

## 命令

```bash
# 创建/同步虚拟环境与所有依赖组
uv sync --all-groups

# 从成员交付生成标准化记录、来源注册和治理汇总
uv run python scripts/import_deliverables.py --clean

# 对成员交付做只读哈希、完全重复检测和记录质量门禁
python3 scripts/run_pipeline.py --clean --input-root datasets

# 预览已批准采集目标（无网络请求）
python3 scripts/collect_sources.py --target COLLECT-DRONERF-GITHUB --dry-run

# 采集公开元数据；脚本会使用 ETag / Last-Modified 做增量请求
python3 scripts/collect_sources.py --target COLLECT-DRONERF-GITHUB

# 从成员一、二只读交付完整重建导入、治理、门禁、看板与测试
python3 scripts/run_all.py

# 对人员二提供的受控小样本做独立本地验收；解压到 staging，不修改 datasets 原件
python3 scripts/run_data_pipeline.py

# 对已逐文件审查且填写哈希/大小/许可的外部工件执行受控下载
python3 scripts/download_artifacts.py --target <TARGET_ID> --allow-download

# 基础回归测试
python3 -m unittest discover -s tests -v
```

## 证据和质量要求

- 每个 `source_id` 必须能在 `configs/sources/sources.json` 找到。
- 型号关键声明必须包含原文摘录 `quote` 和页码/章节/段落 `locator`。
- 所有许可未知、研究限定、非商业或禁止再分发情形均应保留为风险，不能推断为开放许可。
- 不确定的传感器参数、同步语义、监管状态使用 `UNKNOWN`、`PARTIAL` 或冲突记录；禁止将推测写成事实。
- 以 SHA-256 相同认定“完全重复”；近似重复必须另行人工复核。
- `PASS_WITH_WARNINGS` 不代表可公开发布或可再分发。

## 导入与 Schema

- `scripts/import_deliverables.py` 只转换现有成员交付，详细数据卡 / Excel 仍是上游审计证据。
- `scripts/build_governance.py` 生成交付哈希清单、关系、冲突、缺口/许可看板和复现性审计。它不能将成员二的验证报告视为人员四独立重现；只有本地原始样本及重算输出存在时，才可写 `independent_download_or_file_read_performed_by_person4: true`。
- `datasets/member2_controlled_samples/` 是受控小样本交付原件，保持只读。`scripts/reproduce_samples.py` 仅解压到 `data/staging/controlled_samples/` 并输出复现记录；`scripts/publish_curated_index.py` 仅发布可追溯的元数据索引，不能将受限 raw 载荷复制到 `data/curated/`。
- `scripts/download_artifacts.py` 的下载必须同时满足配置中的 `approved: true`、`allow_download: true`、明确 HTTPS URL、正的 `max_bytes`、预期 SHA-256，以及命令行 `--allow-download`。不接受省略哈希的“先下载后验收”。
- `scripts/validate_downloaded_artifacts.py` 目前针对已接收的 DroneRF 官方 Mendeley RAR 文件列举目录、抽取 segment 0 并与受控样本哈希比对；它不宣称全量 CSV 的语义或标签已经逐项复验。
- 修改 `schemas/` 或模板时，同时更新导入器、测试和 README。
- 新增采集器前需审阅目标站点访问条款、robots、认证和许可；不得绕过访问控制、验证码或下载限制。
- `scripts/collect_sources.py` 仅对 `enabled` 或明确 `--target` 的目标运行。默认仅采集元数据；实际网页/PDF/附件落盘还须目标配置为 `allow_download: true` 且命令明确传入 `--allow-download`。
- GitHub 使用官方 REST API；Zenodo 使用官方 records API；Mendeley 使用公开数据集 API。FCC/FAA 仅归档人工确认的公开结果 URL，不自动提交查询表单。

## Git / GitHub

- 提交生成的轻量记录、Schema、脚本、文档、哈希清单和报告；不提交密钥、令牌、cookie、个人下载路径或大数据包。
- 提交前运行上述测试和导入/流水线命令。
- 这里的 GitHub 既可能指代码远程，也可能指开源资料来源。**资料采集**统一走 `collect_sources.py`；代码远程推送仅在用户明确要求时执行。
