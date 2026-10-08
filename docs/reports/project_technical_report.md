# 无人机资料与多模态数据项目技术报告

- **项目**：无人机资料与多模态数据工程底座
- **阶段日期**：2026-10-08
- **参与角色**：人员一（型号资料）、人员二（多模态数据集）、人员三（关联资料与治理）、人员四（数据工程与质量核验）
- **报告性质**：阶段技术报告；仅基于仓库中现有交付、机器生成物和实际执行记录。

## 摘要

项目目标是将分散的无人机型号资料、监管/认证证据、多模态公开数据集、关联关系和安全/供应链资料，组织为可追溯、可复现、许可可见、可持续更新的数据资产。当前阶段已形成两层数据治理能力：

1. **交付物治理层**：将成员一、二资料标准化，保留证据和来源，生成关系、冲突、缺口、哈希清单、质量报告和静态看板；
2. **真实数据验收层**：对获准的小样本和公开原件进行受控下载、哈希比对、格式/关联检查、解压抽检和受控发布索引。

已实现 4 个型号、36 条型号证据、3 张数据集卡、25 个来源、29 条标准化关系和 2 条冲突登记。成员交付当前质量门禁为 0 ERROR、4 WARNING、`PASS_WITH_WARNINGS`。三个受控小样本独立复验均为 `PASS_WITH_WARNING`；DroneRF 两个公开官方 RAR 的下载、哈希和 segment 0 抽检为 `PASS`。

## 1. 项目范围与角色协同

| 角色 | 输入 / 真源 | 主要输出 | 与其他角色的接口 |
|---|---|---|---|
| 人员一 | 厂商、规格、说明书、FCC/FAA 资料 | 型号字段、参数、原文定位、来源证据 | 向人员三提供实体/认证依据，向人员四提供结构化导入和采集目标 |
| 人员二 | 多模态数据集、样本、数据卡、验证记录 | 数据集来源、模态、许可、关联规则、样本验证 | 向人员三提供数据集关系，向人员四提供复现计划和受控样本 |
| 人员三 | 来源、实体、关系、论文/开源/安全资料 | 图谱 nodes/edges、哈希、冲突、缺口、许可治理 | 向人员四提供来源/关系/图谱导出和治理规则 |
| 人员四 | 上述交付及批准 URL | 采集器、导入器、校验器、报告、看板、复现记录 | 将事实资料转换为机器可执行流水线和可查询产物 |

协同原则：成员原始交付是事实输入；人员四生成的 JSON、清单和报告是可重建的互操作层，不替代上游原件。

## 2. 总体技术架构

```text
┌───────────────────────────────────────────────────────────────────┐
│ 原始输入层                                                        │
│ datasets/member1_model_research/     型号 Excel                   │
│ datasets/member2_multimodal_datasets/ 数据卡/验证记录             │
│ datasets/member2_controlled_samples/ 受控样本 ZIP                 │
│ datasets/member3_relative_resources/ 来源、关系、图谱、治理 CSV   │
└────────────────────────────┬──────────────────────────────────────┘
                             │ 只读导入 / 审计
┌────────────────────────────▼──────────────────────────────────────┐
│ 标准化与治理层                                                     │
│ import_deliverables.py → models / datasets / evidence / sources   │
│ build_governance.py   → relations / conflicts / dashboard data    │
│ run_pipeline.py       → SHA-256 manifests / duplicate / gate      │
└────────────────────────────┬──────────────────────────────────────┘
                             │ 经审核的 URL / API
┌────────────────────────────▼──────────────────────────────────────┐
│ 采集与原始保全层                                                   │
│ collect_sources.py    → metadata / conditional update state        │
│ download_artifacts.py → raw immutable artifact + receipt           │
└────────────────────────────┬──────────────────────────────────────┘
                             │ 解压 / 内容检查
┌────────────────────────────▼──────────────────────────────────────┐
│ 验收与受控发布层                                                   │
│ reproduce_samples.py          → controlled sample results          │
│ validate_downloaded_artifacts → raw artifact cross-check           │
│ publish_curated_index.py      → curated metadata-only index        │
└───────────────────────────────────────────────────────────────────┘
```

### 数据分层

| 层 | 用途 | 写入规则 |
|---|---|---|
| `datasets/` | 成员交付原件和受控样本 | 只读；不由脚本改写 |
| `data/raw/` | 获批下载的原始文件 | 只增不改；不自动删除 |
| `data/staging/` | 解压、抽取和待验收内容 | 可由脚本重新生成 |
| `data/curated/` | 已通过门禁的受控发布索引 | 当前仅元数据，不默认复制受限载荷 |
| `data/records/` | 标准化实体、关系、冲突 | 机器生成或审核后更新 |
| `data/manifests/` | 文件哈希和去重结果 | 可重建 |
| `data/reports/` | 质量、复现和看板报告 | 可重建 |

## 3. 核心实现

### 3.1 Schema 与标准化导入

Schema/模板覆盖型号、数据集、关系和冲突记录。`import_deliverables.py` 从成员一 Excel 与人员二资料导入结构化记录，当前导入规模：

```text
型号：4
字段证据：36
数据集卡：3
来源：25
```

型号记录保留通信频段、协议、SDK、固件和字段证据；数据集卡保留模态、版本、许可状态、关联键和验证边界。人员三的关系真源仍以其 CSV 图谱导出为准，人员四同时生成了面向看板和验收的 29 条 JSON 关系。

### 3.2 采集与增量更新

`collect_sources.py` 支持 HTTP、GitHub REST API、Zenodo Records API、Mendeley Data API 和监管结果快照。优先使用 `ETag`/`Last-Modified`，无响应验证器时使用规范化元数据 SHA-256 作为增量回退。

实际成功的元数据采集：

- GitHub：DroneRF、MMAUD；
- Mendeley：DroneRF v1，获取 23 个文件的名称、大小、远程 SHA-256 和下载 URL。

当前不能成功的访问被如实记录：DJI 页面在当前网络 TLS 握手超时；Autel PDF HTTP 403；不绕过访问控制。Zenodo 无 record ID；FCC/FAA 无人工确认结果 URL。

### 3.3 受控下载与原始保全

`download_artifacts.py` 对每个下载目标要求：HTTPS URL、来源 ID、预期 SHA-256、正的大小上限、许可状态、`approved: true`、`allow_download: true` 和命令行 `--allow-download`。流程为 TLS 验证→临时 `.partial` 写入→大小限制→哈希重算→原子移动→收据输出。

实际下载成果：

| 文件 | 大小 | SHA-256 | 结果 |
|---|---:|---|---|
| DroneRF `RF Data_10000_L.rar` | 217,760,401 bytes | 与 Mendeley API 一致 | accepted |
| DroneRF `RF Data_10000_H.rar` | 173,545,467 bytes | 与 Mendeley API 一致 | accepted |

### 3.4 归档、去重与质量门禁

`run_pipeline.py` 扫描指定输入根，输出 SHA-256 JSONL/CSV 清单与完全重复组。完全重复定义为 SHA-256 相同；原始层不自动删除任何副本。

当前成员交付运行结果：

```text
files_scanned: 126
exact_duplicate_groups: 1  # 人员三哈希目录中的同内容双清单；原件均保留
records_validated: 38
ERROR: 0
WARNING: 4
gate_status: PASS_WITH_WARNINGS
```

4 个 Warning 均对应厂商型号记录的来源许可状态未知，不是文件损坏或字段结构错误。`--include-fixtures` 用于测试门禁，含故意不合规的示例数据，预期得到 `FAIL`，不可与真实交付结果混淆。

### 3.5 小样本复现与内容校验

`reproduce_samples.py` 以 `sample_manifest.json` 和 `SHA256.txt` 为核对基准，对人员二三个受控 ZIP 完成哈希、大小、完整性和内容检查：

| 数据集 | 内容检查 | 独立结果 |
|---|---|---|
| Anti-UAV300 | MP4 ISO-BMFF 结构、JSON 可解析、标注帧数 493/493 | `PASS_WITH_WARNING` |
| DroneRF | L/H CSV、无头 1×10,000,000 数值矩阵、BUI/segment 命名关系 | `PASS_WITH_WARNING` |
| MMAUD | PNG、NPY header、`seq0001` 最近时间戳 | `PASS_WITH_WARNING` |

三者的共同 Warning 是交付内 `delivery_summary.json` 与实际包、`sample_manifest.json`、`SHA256.txt` 的哈希/大小冲突。实际包与后两者一致；系统不静默覆盖该冲突。

`validate_downloaded_artifacts.py` 还对已下载的 DroneRF RAR 进行目录列举（各 22 成员）、指定 segment 抽取和哈希比对。抽取的 `10000L_0.csv`、`10000H_0.csv` 与受控样本对应文件 SHA-256 完全一致，结果 `PASS`。

### 3.6 看板、关系与冲突

`build_governance.py` 输出：

```text
data/reports/governance_dashboard.html
data/normalized/governance_dashboard_data.json
data/records/relations/
data/records/conflicts/
data/delivery_manifest.json
```

静态看板展示型号/数据集/证据/来源统计、型号缺口、许可状态和解释边界。当前 2 条冲突记录涉及 MMAUD 名称与不同验证范围的就绪状态。人员三另有更广覆盖的 CSV 图谱导出（53 来源、61 实体、76 全量边、59 对外高置信边），待建立稳定的自动映射接入。

## 4. 可复现运行说明

```bash
cd data-collector
uv sync --all-groups

# 静态检查
uv run ruff check scripts tests

# 成员交付治理重建：不联网
uv run python scripts/run_all.py

# 受控样本复现、DroneRF 下载原件抽检与治理重建
uv run python scripts/run_data_pipeline.py

# 采集公开元数据
uv run python scripts/collect_sources.py --target COLLECT-DRONERF-MENDELEY
```

## 5. 风险、限制与待办

| 优先级 | 项目级问题 | 当前状态 | 建议 |
|---|---|---|---|
| P0 | 人员二 `delivery_summary.json` 与最终 ZIP 不一致 | 3 个复现结果均 Warning | 人员二重生成或确认摘要 |
| P0 | FCC/FAA 监管原始结果 | 缺官方 URL/ID，且 FCC 网络受阻 | 人员一/三提供经确认 URL；人员四快照归档 |
| P0 | 厂商 PDF/许可条款 | DJI 超时、Autel 403、许可证未知 | 审阅条款，提供替代官方入口或人工下载件 |
| P1 | 全量多模态内容验证 | 仅样本和 DroneRF segment 0 已独立验证 | 分批下载并做完整格式/标签/统计检查 |
| P1 | 人员三图谱与人员四 JSON 的自动对接 | 当前两层并存 | 固化 ID/谓词映射并实现 CSV 导入 |
| P1 | 参数深度清洗 | 多数仍为可追溯字符串 | 拆分数值、单位、条件、官方/推导状态 |
| P2 | 动态看板/Graph API | 当前为静态 HTML/JSON | 选择数据库/API/前端并实现筛选与权限 |

## 6. 阶段结论

项目已从分散资料收集推进到可重复的治理和验收工程：成员交付可标准化和审计，受控样本可独立复验，部分公开原件已下载并与样本交叉验证。当前阶段的核心限制是上游监管材料、厂商访问/许可、Zenodo 标识以及全量数据可得性；这些限制已被记录为可追踪缺口，而非以推测补齐。下一阶段应优先收口摘要冲突、监管证据和图谱映射，再扩展全量内容验证与动态查询服务。
