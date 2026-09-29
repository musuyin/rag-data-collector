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

## 命令

```bash
# 从成员交付生成标准化记录、来源注册和治理汇总
python3 scripts/import_deliverables.py --clean

# 对成员交付做只读哈希、完全重复检测和记录质量门禁
python3 scripts/run_pipeline.py --clean --input-root datasets

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
- 修改 `schemas/` 或模板时，同时更新导入器、测试和 README。
- 新增采集器前需审阅目标站点访问条款、robots、认证和许可；不得绕过访问控制、验证码或下载限制。

## Git / GitHub

- 提交生成的轻量记录、Schema、脚本、文档、哈希清单和报告；不提交密钥、令牌、cookie、个人下载路径或大数据包。
- 提交前运行上述测试和导入/流水线命令。
- GitHub 推送仅在远程仓库已确认、内容不含受限数据且访问权限正确时执行。
