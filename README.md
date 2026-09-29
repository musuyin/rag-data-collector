# 无人机资料与多模态数据工程底座（人员四）

> **定位**：面向无人机型号资料、监管证据和多模态数据集的“定向采集 + 原始归档 + 自动验收 + 治理展示”工具链。  
> **原则**：`datasets/` 保留成员交付原件并保持只读；真实下载文件进入 `data/raw/`；所有结论附来源、版本、哈希、范围和许可边界。

---

## 导航看板

| 任务职责 | 实现入口 | 当前状态 | 关键产物 / 实际结果 |
|---|---|---|---|
| [1. 定向采集与增量更新](#1-定向采集工具) | `scripts/collect_sources.py`、`scripts/download_artifacts.py` | **部分完成** | GitHub/Mendeley 元数据已实际采集；DroneRF 两个官方 RAR 已实际下载并验收；DJI 网络超时、Autel PDF 为 403；Zenodo/FCC/FAA 等待正式 ID/结果 URL。 |
| [2. 归档与去重](#2-归档与去重流水线) | `scripts/run_pipeline.py` | **已完成** | SHA-256、文件清单、完全重复检测；当前成员交付扫描 50 文件、0 完全重复组。 |
| [3. 质量门禁与自动校验](#3-质量门禁与自动校验) | `scripts/run_pipeline.py`、`scripts/reproduce_samples.py` | **已完成基础验收** | 当前真实交付：0 ERROR、4 WARNING、`PASS_WITH_WARNINGS`；小样本内容验收已实现。 |
| [4. 数据卡与字段模板工程化](#4-数据卡与字段模板工程化) | `schemas/`、`templates/`、`scripts/import_deliverables.py` | **已完成** | 4 型号、36 证据、3 数据集、25 来源被标准化。 |
| [5. 数据看板](#5-数据看板) | `scripts/build_governance.py` | **已完成静态原型** | `data/reports/governance_dashboard.html` + 可查询 JSON。 |
| [6. 小样本复现性验证](#6-复现性验证) | `scripts/reproduce_samples.py`、`scripts/validate_downloaded_artifacts.py` | **已完成受控样本 / 部分全量原件验证** | 三个受控 ZIP 为 `PASS_WITH_WARNING`；DroneRF 官方 RAR 抽检为 `PASS`。 |

---

## 运行环境

使用 **`pyproject.toml` + `uv.lock`** 管理依赖；不要新建 `requirements.txt`。

- Python：`>=3.12`
- `uv`：创建 `.venv`、解析依赖、锁定精确版本
- 运行依赖：`certifi`（HTTPS CA 证书验证）
- 开发依赖：`ruff`（静态检查）

```bash
cd data-collector
uv sync --all-groups
```

推荐始终通过 `uv run` 执行：

```bash
uv run python scripts/run_all.py
```

依赖变更规则：修改 `pyproject.toml` 后运行 `uv lock && uv sync --all-groups`；提交 `uv.lock`，不提交 `.venv/` 或 `.uv-cache/`。

---

## 数据分层与处理边界

```text
datasets/                              成员原始交付 / 受控小样本原件：只读，不移动、不修改
data/raw/                              已批准外部下载原件：只增不改
data/staging/                          从 ZIP/RAR 解压或抽取的可重建验收工作区
data/curated/                          只发布通过门禁的可追溯索引；不默认复制受限原始载荷
data/records/                          标准化型号、数据集、关系、冲突记录
data/normalized/                       证据、进度、看板查询数据
data/manifests/                        SHA-256 清单和重复检测结果
data/reports/                          质量、复现、下载验收、治理看板报告
data/samples/                          受控小样本复现结果和下载抽检结果
```

处理流：

```text
成员交付 datasets/
  → 导入 / Schema 化 / 治理
  → records + normalized + manifests + reports

审核 URL / 公开 API
  → 元数据采集 → 逐文件批准下载 → data/raw/
  → 格式、哈希、标签/关联校验 → data/staging/
  → 受控发布索引 → data/curated/
```

---

# 1. 定向采集工具

## 目标与实现

支持以下来源适配器：

| 来源 | 适配器 | 增量策略 | 当前实现状态 |
|---|---|---|---|
| 厂商官网 / 公开 PDF | `http` | `ETag` / `Last-Modified` | 已实现；DJI 当前 TLS 握手超时，Autel PDF 返回 HTTP 403，未绕过限制。 |
| GitHub | `github_repo` | GitHub API 条件请求 + 元数据摘要 | 已实际采集 DroneRF、MMAUD 仓库元数据。 |
| Mendeley Data | `mendeley_dataset` | 条件请求；无验证器时元数据 SHA-256 回退 | 已实际采集 DroneRF v1、23 个文件名/大小/远程 SHA-256/下载 URL。 |
| Zenodo | `zenodo_record` | Records API 条件请求 | 适配器已实现；尚无真实 `record_id`。 |
| FCC / FAA | `regulatory_snapshot` | 人工确认结果 URL 的快照增量检查 | 适配器已实现；尚无人工确认的官方结果 URL。 |

元数据配置：

```text
configs/collection_targets.json
configs/sources/sources.json
```

常用命令：

```bash
# 预览目标，不发网络请求
uv run python scripts/collect_sources.py --target COLLECT-DRONERF-GITHUB --dry-run

# 采集公开元数据（不下载正文/附件）
uv run python scripts/collect_sources.py --target COLLECT-DRONERF-GITHUB
uv run python scripts/collect_sources.py --target COLLECT-DRONERF-MENDELEY
```

输出：

```text
data/collection_state.json             # ETag / Last-Modified / 检查时间 / 增量状态
data/collection_metadata/              # 规范化元数据和远程文件清单
```

## 受控下载与下载收据

下载器不会“见 URL 就下载”。每个文件必须先在 `configs/download_targets.json` 明确：

```text
HTTPS URL、source_id、预期 SHA-256、max_bytes、许可证、approved: true、allow_download: true
```

然后才可运行：

```bash
uv run python scripts/download_artifacts.py --target <TARGET_ID> --allow-download
```

下载器执行 TLS 验证、大小上限、`.partial` 临时写入、SHA-256 重算和原子归档；仅哈希吻合才写入 `data/raw/downloaded/`，并生成：

```text
data/receipts/downloads/
```

### 已实际下载的真实数据

DroneRF 的两个 Mendeley Data v1 官方 RAR 已成功下载：

| 文件 | HTTP | 大小 | 官方 SHA-256 比对 | 归档状态 |
|---|---:|---:|---|---|
| `RF Data_10000_L.rar` | 200 | 217,760,401 bytes | 一致 | accepted |
| `RF Data_10000_H.rar` | 200 | 173,545,467 bytes | 一致 | accepted |

许可：`CC BY 4.0`。原件位于 `data/raw/downloaded/`（被 Git 忽略），每个文件均有下载收据。

## 未完成与阻塞

- Zenodo：需要真实 record ID 与已登记来源；
- FCC/FAA：需要人工确认的官方公开结果 URL、型号/FCC ID/Remote ID 关联依据；
- 厂商资料：需要网络可达且条款允许的正式下载；当前 DJI 超时、Autel 403；
- 其他 Mendeley/Google Drive 文件：需逐文件明确许可、大小上限、远程 SHA-256 并批准后下载。

不自动提交监管查询表单，不绕过 CAPTCHA、认证、robots、403 或下载限制。

---

# 2. 归档与去重流水线

入口：

```bash
# 对成员交付只读盘点
uv run python scripts/run_pipeline.py --clean --input-root datasets

# 对指定真实原始数据目录扫描
uv run python scripts/run_pipeline.py --clean --input-root data/raw
```

实现内容：

- 统一相对路径、文件大小、MIME 推断和 SHA-256；
- 原始层不自动删除文件；SHA-256 相同仅登记为完全重复；
- 输出 JSONL、CSV 和重复组，结果可复算；
- 对所有输入根目录保持只读扫描。

机器生成产物：

```text
data/manifests/file_manifest.jsonl
data/manifests/file_manifest.csv
data/manifests/duplicates.json
data/delivery_manifest.json             # 成员交付保全清单
```

当前真实成员交付扫描结果：

```text
files_scanned: 50
exact_duplicate_groups: 0
```

> `--include-fixtures` 是测试模式，会加载故意不合规的 fixture 记录并预期产生 `FAIL`；不要把该结果视为真实成员交付质量。

---

# 3. 质量门禁与自动校验

入口：

```bash
uv run python scripts/run_pipeline.py --clean --input-root datasets
```

门禁覆盖：

| 校验类别 | 已实现检查 |
|---|---|
| 字段完整性 | JSON 可解析、必填字段、枚举、记录类型、Schema 子集校验 |
| 可追溯性 | `source_id` 必须登记；型号关键字段需证据摘录和定位 |
| 原始文件 | SHA-256、大小、MIME 推断、完全重复组 |
| ZIP / RAR / 样本格式 | ZIP 完整性、安全解压；RAR 列表/指定成员抽取；PNG、NPY、CSV、MP4 结构检查 |
| 标签与关联 | Anti-UAV300 JSON 与 RGB/IR 标注帧数；DroneRF L/H + BUI/segment；MMAUD sequence/timestamp 最近邻 |
| 风险与冲突 | 许可未知 Warning、结构化冲突记录、受控交付摘要不一致 Warning |

结果分级：

```text
PASS                 无 ERROR / WARNING
PASS_WITH_WARNINGS   无 ERROR，但需要人工处置
FAIL                 存在 ERROR；不得进入 curated
```

当前真实交付门禁：

```text
records_validated: 38
ERROR: 0
WARNING: 4
status: PASS_WITH_WARNINGS
```

4 个 Warning 都是四个厂商型号资料的 `license_status: unknown`，不代表数据损坏。

输出：

```text
data/reports/quality_report.md
data/reports/quality_report.json
data/reports/pipeline_summary.json
```

---

# 4. 数据卡与字段模板工程化

## Schema 与模板

```text
schemas/model_record.schema.json
schemas/dataset_card.schema.json
schemas/relation_record.schema.json
schemas/conflict_record.schema.json

templates/model_record.json
templates/dataset_card.json
templates/relation_record.json
templates/conflict_record.json
```

## 成员交付导入

```bash
uv run python scripts/import_deliverables.py --clean
uv run python scripts/build_governance.py --clean
```

输入保持在 `datasets/`：

```text
member1_model_research/*.xlsx
member2_multimodal_datasets/
```

当前已导入：

| 类型 | 数量 | 输出 |
|---|---:|---|
| 型号记录 | 4 | `data/records/imported/models/` |
| 型号字段证据 | 36 | `data/normalized/evidence.jsonl` |
| 数据集卡 | 3 | `data/records/imported/datasets/` |
| 来源登记 | 25 | `configs/sources/sources.json` |
| 图关系 | 29 | `data/records/relations/` |
| 冲突记录 | 2 | `data/records/conflicts/` |

数据卡已固化 MMAUD、Anti-UAV300、DroneRF 的模态、关联键、许可风险、样本验证范围和来源。

---

# 5. 数据看板

入口：

```bash
uv run python scripts/build_governance.py --clean
```

展示入口：

```text
data/reports/governance_dashboard.html
```

可查询数据：

```text
data/normalized/governance_dashboard_data.json
```

当前静态看板包含：

- 型号、数据集、证据、来源、成员交付文件总量；
- 型号资料完成度和缺口；
- 数据集模态、许可和验证状态；
- 治理风险与事实解释边界。

当前为静态 HTML / JSON 原型；动态筛选、API、Graph 数据库和多人权限管理属于后续增强项。

---

# 6. 复现性验证

## 受控小样本独立复现

人员二提供的三个真实小样本包：

```text
datasets/member2_controlled_samples/packages/
```

运行：

```bash
uv run python scripts/reproduce_samples.py --clean
# 或包含治理重建的一键流程
uv run python scripts/run_data_pipeline.py
```

脚本不会修改 `datasets/` 原件；会安全解压到 `data/staging/controlled_samples/`，并生成：

```text
data/samples/reproduction_results/{Anti-UAV300,DroneRF,MMAUD}.json
data/reports/reproduction_{Anti-UAV300,DroneRF,MMAUD}.md
data/curated/controlled_samples/index.json
```

实际结果：

| 数据集 | 包哈希 / ZIP | 内容复验 | 状态 |
|---|---|---|---|
| Anti-UAV300 | 实际 ZIP 同时匹配 `sample_manifest.json` 与 `SHA256.txt` | visible/infrared MP4 结构存在；2 个标注 JSON 可解析，帧数为 493 / 493 | `PASS_WITH_WARNING` |
| DroneRF | 同时匹配两个清单 | L/H 文件均为 1×10,000,000 数值矩阵；BUI 10000 / segment 0 关联成立 | `PASS_WITH_WARNING` |
| MMAUD | 同时匹配两个清单 | PNG + 3 个 NPY 可读；相对 Camera 的 LiDAR/Livox/Radar 差为 5.788/8.224/4.836 ms | `PASS_WITH_WARNING` |

三个 Warning 的统一原因：`delivery_summary.json` 中记录的大小与 SHA-256 均与实际 ZIP、`sample_manifest.json`、`SHA256.txt` 不一致。当前以“实际包 + 两个一致清单”为验收依据，但保留警告，等待成员二更新/确认摘要文件。

边界：MP4 当前做 ISO-BMFF `ftyp` 结构检查，不等价于逐帧媒体解码；MMAUD 证明的是该样本的路径/格式/最近时间戳关联，不等价于标定、硬件同步或全量数据集验收。

## 已下载 DroneRF 原件的交叉验证

```bash
uv run python scripts/validate_downloaded_artifacts.py --clean
```

已实际完成：

1. 列出两个官方 RAR 的目录，各有 22 个成员；
2. 从每个 RAR 抽取 `10000[L/H]_0.csv`；
3. 计算抽取文件 SHA-256；
4. 与人员二受控小样本中对应 CSV 比对。

结果：两个抽取 CSV 均与受控小样本**SHA-256 完全一致**，下载原件验证为：

```text
PASS
```

产物：

```text
data/samples/download_validation_results/DroneRF_10000_LH.json
data/reports/download_validation_DroneRF_10000_LH.md
```

---

## 一键命令索引

```bash
# 静态检查
uv run ruff check scripts tests

# A：成员交付 → 标准化记录、治理、质量报告、看板、单元测试（不联网）
uv run python scripts/run_all.py

# B：受控小样本复现 + curated 元数据索引 + 已下载 DroneRF 抽检 + 治理重建
uv run python scripts/run_data_pipeline.py

# 元数据采集（示例）
uv run python scripts/collect_sources.py --target COLLECT-DRONERF-MENDELEY

# 执行单个已经审核并带预期哈希的下载目标
uv run python scripts/download_artifacts.py --target DOWNLOAD-DRONERF-RF-DATA-10000-L --allow-download

# 复验已下载 DroneRF RAR
uv run python scripts/validate_downloaded_artifacts.py --clean
```

---

## 主要成果清单

```text
采集与校验脚本集
  scripts/collect_sources.py
  scripts/download_artifacts.py
  scripts/reproduce_samples.py
  scripts/validate_downloaded_artifacts.py
  scripts/run_pipeline.py
  scripts/import_deliverables.py
  scripts/build_governance.py

哈希与去重清单（机器生成）
  data/manifests/file_manifest.jsonl
  data/manifests/file_manifest.csv
  data/manifests/duplicates.json
  data/delivery_manifest.json

质量与验收报告
  data/reports/quality_report.md
  data/reports/reproduction_*.md
  data/reports/download_validation_DroneRF_10000_LH.md
  data/receipts/downloads/

数据看板原型
  data/reports/governance_dashboard.html
  data/normalized/governance_dashboard_data.json

小样本复现验证记录
  data/samples/reproduction_results/
  data/samples/download_validation_results/
  data/curated/controlled_samples/index.json
```

---

## 交付前仍需推进的事项

1. **修复成员二交付摘要**：更新 `datasets/member2_controlled_samples/delivery_summary.json`，使其大小与 SHA-256 与实际 ZIP、`sample_manifest.json`、`SHA256.txt` 一致；之后三项可从 `PASS_WITH_WARNING` 升为 `PASS`。
2. **厂商与监管证据**：提供可访问且已审查条款的厂商 PDF、FCC/FAA 官方结果 URL、型号关联依据。
3. **Zenodo 接入**：提供正式 `record_id` 和来源登记。
4. **完整内容验证**：对获批的更多原始包完成完整解压、图像/视频逐帧读取、RF/标签统计、点云和雷达语义校验；当前仅对规定样本和 DroneRF segment 0 做到独立验证。
5. **语义清洗与发布**：将型号字符串参数深度拆分为数值、单位、条件和证据等级；建立正式 `curated/` 发布版本、动态查询 API 和看板筛选。

## 协作与合规

- `datasets/` 与 `data/raw/` 不自动删除、覆盖或重命名原件；
- SHA-256 相同仅标记完全重复，保留每个来源上下文；
- 许可证未知、非商业、研究用途或禁止再分发必须保留风险标记；
- 不绕过认证、验证码、robots、站点访问控制或使用条款；
- GitHub 在这里指资料来源采集，不表示任何代码远程推送；除非用户明确要求，不执行远程 Git 操作。
