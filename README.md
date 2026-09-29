# 无人机资料与多模态数据工程底座（人员四）

本项目提供在尚未取得真实厂商、监管和数据集资料前即可运行的数据治理基础能力：

- 原始文件归档扫描与 SHA-256 清单；
- 完全重复文件检测（仅标记，不删除原文件）；
- 结构化来源、型号资料、数据集卡、关系和冲突记录模板；
- 基于 JSON Schema 子集的字段完整性与可追溯性质量门禁；
- 机器可读 JSON/JSONL/CSV 清单及 Markdown 报告；
- 后续可扩展的来源注册表和采集配置。

## 快速开始

仅需要 Python 3.11+，无第三方依赖：

```bash
cd data-collector
python3 scripts/run_pipeline.py --include-fixtures
```

这会扫描 `data/raw/` 及 `fixtures/raw/`，并在 `data/manifests/`、`data/reports/` 产生：

- `file_manifest.jsonl` / `file_manifest.csv`：文件、哈希和来源关联清单；
- `duplicates.json`：完全重复文件组；
- `quality_report.json` / `quality_report.md`：结构化记录的质量门禁结果；
- `pipeline_summary.json`：本次运行的汇总和可复现参数。

真实资料到位后，将原始文件放到 `data/raw/<source_type>/`，填写 `data/records/` 下的记录，并执行：

```bash
python3 scripts/run_pipeline.py
```

如需先对成员交付目录（例如当前的 `datasets/`）进行只读盘点、哈希和完全重复检查，不移动文件：

```bash
python3 scripts/run_pipeline.py --input-root datasets
```

## 目录约定

```text
configs/sources/          来源注册与采集配置（不存放密钥）
schemas/                  结构化记录的字段规范（JSON Schema）
templates/                可复制填写的 JSON 模板
data/raw/                 原始归档文件：只增不改
data/staging/             解压、转换、待核验文件
data/curated/             通过门禁后的数据（后续流程写入）
data/records/             人工或采集器生成的结构化记录
data/manifests/           机器生成哈希清单和去重结果
data/reports/             机器生成质量报告
data/samples/             小样本复现记录
fixtures/                 可提交的演示数据，验证流水线；非真实资料
scripts/                  流水线与后续采集脚本
```

## 记录文件与质量门禁

每条 JSON 记录应符合 `schemas/` 中对应定义，并且至少应有：

- `source_id`：必须存在于 `configs/sources/sources.json`；
- `download_url` 或等价的可追溯入口（取决于记录类型）；
- 许可状态；
- 对性能、频段、固件等关键声明：原文摘录及页码或段落定位；
- `record_status`：`draft`、`reviewed` 或 `approved`。

质量结果：

- **ERROR**：阻止进入 `curated/`；
- **WARNING**：允许暂存，但应人工确认；
- **INFO**：仅提示。

## 当前已导入的成员交付

`datasets/` 当前包含成员一和成员二的阶段性交付，项目提供只读导入器：

```bash
python3 scripts/import_deliverables.py --clean
python3 scripts/run_pipeline.py --clean --input-root datasets
```

导入后生成：

- `data/records/imported/models/`：4 个型号的标准化记录；
- `data/records/imported/datasets/`：MMAUD、Anti-UAV300、DroneRF 的互操作数据卡；
- `data/normalized/evidence.jsonl`：人员一的逐条证据；
- `data/normalized/collection_progress.json`：型号资料收集进度；
- `data/normalized/governance_summary.json`：许可、缺口和来源治理汇总；
- `configs/sources/sources.json`：由成员交付登记并规范化的来源注册表。

导入过程不修改 `datasets/`。这些记录是查询和门禁用的标准化层；成员一的 Excel、成员二的详细数据卡和验证报告仍是上游审计证据。

## 与其他成员的交接

- 人员一：从 `templates/model_record.json` 填写型号资料；每个关键参数附 `evidence_quote` 和 `evidence_locator`。
- 人员二：从 `templates/dataset_card.json` 填写数据卡和 `data/samples/` 中的小样本验证记录。
- 人员三：维护来源登记、关系记录和冲突登记；来源 ID 必须先写入 `configs/sources/sources.json`。
- 人员四：以 `scripts/run_pipeline.py` 固化归档、去重、门禁和报告；真实 URL 确定后再在 `scripts/collectors/` 增加受条款约束的来源适配器。

## Git / GitHub 同步

当前项目已具备 Git 提交所需的轻量代码、规范、标准化记录和哈希报告。同步前请确认远程组织、仓库名称和数据访问策略；完整原始数据集、受限许可文件、令牌和 cookie 不得提交。

```bash
# 首次初始化（仅在确认目标仓库后）
git init
git add .
git commit -m "feat: bootstrap drone data governance pipeline"
gh repo create <owner>/<repo> --private --source=. --remote=origin --push

# 后续同步
git add .
git commit -m "chore: import member deliverables and refresh reports"
git push -u origin main
```

也可先创建私有远程仓库，再执行 `git remote add origin <url>` 和 `git push -u origin main`。详见 `AGENTS.md` 的敏感数据和许可限制。

## TODO（按实施顺序）

- [x] 建立目录、命名和记录模板规范。
- [x] 实现 SHA-256、清单、完全重复识别和质量门禁。
- [x] 提供演示夹具、机器生成报告和复现命令。
- [x] 将当前人员一 Excel 转换为型号记录、逐条证据和进度治理汇总。
- [x] 将当前人员二的 MMAUD、Anti-UAV300、DroneRF 数据卡转换为统一数据集记录和来源登记。
- [ ] 与人员一确认型号资料必填字段、单位和证据定位标准。
- [ ] 与人员二确认各模态标签规则、最小样本验证字段和预期结论。
- [ ] 与人员三确认全局来源 ID、实体 ID、关系类型、许可枚举和冲突处置规则。
- [ ] 接入 GitHub、Zenodo 等有明确下载 API/条款的采集器，并支持 ETag/Last-Modified 增量更新。
- [ ] 依据获批的厂商/FCC/FAA 入口实现定向适配器；不得绕过访问控制或违反站点条款。
- [ ] 增加格式/标签深度校验、近似重复检测和可查询数据看板。
