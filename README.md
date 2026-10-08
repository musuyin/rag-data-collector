# 无人机资料与多模态数据工程项目

> **项目目标**：把无人机型号资料、监管证据、多模态数据集、关联关系和安全/供应链资料，建设为可追溯、可复现、许可可见、可持续更新的数据资产。
> **阶段定位**：四名成员分别提供领域事实资料、数据集资料、关联治理资料和工程验收能力；本仓库是统一的归档、标准化、采集、验收和展示入口。

## 项目导航看板

| 角色 | 职责 | 阶段状态 | 个人总结 |
|---|---|---|---|
| 人员一 | 无人机型号与结构化资料 | 已交付 4 个型号、36 条字段证据；监管证据/部分说明书待补 | [人员一总结](docs/reports/member1_model_data_summary.md) |
| 人员二 | 多模态数据集 | 已交付 Anti-UAV300、DroneRF、MMAUD 数据卡、验证记录和受控样本；样本已复验 | [人员二总结](docs/reports/member2_multimodal_datasets_summary.md) |
| 人员三 | 关联资料与数据治理 | 已交付来源、实体、关系、哈希、冲突、缺口和图谱导出；待与工程层联调 | [人员三总结](docs/reports/member3_governance_summary.md) |
| 人员四 | 数据工程与质量核验 | 已实现采集、下载、归档、门禁、看板和样本复现流水线 | [人员四总结](docs/reports/member4_engineering_quality_summary.md) |

- **完整技术说明**：[项目技术报告](docs/reports/project_technical_report.md)
- **治理看板原型**：[`data/reports/governance_dashboard.html`](data/reports/governance_dashboard.html)
- **看板查询数据**：[`data/normalized/governance_dashboard_data.json`](data/normalized/governance_dashboard_data.json)

---

## 一、分工与交付

### 人员一：无人机型号与结构化资料

负责厂商官网、产品页、说明书、规格书以及 FAA/FCC 等监管认证资料；提取型号、性能、核心部件、通信频段、协议、固件和 SDK 信息，并以原文页码或段落形成字段候选、来源和证据清单。

当前原始交付：

```text
datasets/member1_model_research/无人机型号与结构化资料调研.xlsx
```

当前已标准化：4 个型号、36 条字段证据。主要缺口是 FCC/FAA 官方记录、部分说明书和来源条款。

### 人员二：多模态数据集

负责图像、视频、红外、声音、射频、雷达、轨迹和飞行日志资料；维护 Anti-UAV300、DroneRF、MMAUD 等数据集的规模、格式、标签、许可、采集环境和样本验证。

当前原始交付：

```text
datasets/member2_multimodal_datasets/
datasets/member2_controlled_samples/
```

当前已完成 3 张标准化数据集卡和三个受控小样本复验。DroneRF 两个官方 Mendeley RAR 已实际下载，并与受控样本 segment 0 完成交叉哈希验证。

### 人员三：关联资料与数据治理

负责厂商—型号—部件—软件—协议—漏洞关系、论文/开源/安全公告/供应链资料、来源登记、哈希、重复、冲突、缺口、许可和图谱导出。

当前原始交付：

```text
datasets/member3_relative_resources/
```

人员三阶段报告声明：53 个来源、61 个实体、76 条全量边、59 条可对外展示的高置信边、19 个哈希归档文件，CSV 校验通过。其 CSV 图谱真源待接入工程化 JSON/Graph 导入流程。

### 人员四：数据工程与质量核验

负责将前三位成员的交付变为可重复执行的工程能力：定向采集、受控下载、SHA-256 归档、去重、结构化导入、质量门禁、复现性验证、关系/冲突治理和看板。

工程脚本位于：

```text
scripts/
configs/
schemas/
templates/
```

---

## 二、数据流与目录约定

```text
成员交付（datasets/，只读）
  ├─ 人员一：型号 Excel
  ├─ 人员二：数据卡、验证记录、受控样本 ZIP
  └─ 人员三：来源、关系、哈希、冲突、图谱 CSV
          ↓
标准化与治理（data/records、data/normalized、data/manifests、data/reports）
          ↓
已审核来源 URL / API
          ↓
受控下载（data/raw，只增不改）
          ↓
解压与内容验收（data/staging，可重建）
          ↓
受控发布索引（data/curated，当前不复制受限原始载荷）
```

| 目录 | 用途 | 规则 |
|---|---|---|
| `datasets/` | 四名成员的原始交付 | 只读，不由处理脚本改写 |
| `data/raw/` | 已批准下载的原始文件 | 只增不改，原件不自动删除 |
| `data/staging/` | 解压、抽取、转换、待验收内容 | 可重新生成 |
| `data/curated/` | 通过门禁的受控发布数据/索引 | 当前发布元数据索引，不默认复制受限载荷 |
| `data/records/` | 标准化实体、关系、冲突 | 可由导入/治理脚本重建 |
| `data/manifests/` | SHA-256 与重复检测 | 可重建 |
| `data/reports/` | 质量、复现和看板报告 | 可重建 |

---

## 三、当前阶段成果

| 指标 | 当前结果 |
|---|---:|
| 标准化型号 | 4 |
| 型号字段证据 | 36 |
| 标准化数据集卡 | 3 |
| 来源登记（工程层） | 25 |
| 标准化关系（工程层） | 29 |
| 冲突登记（工程层） | 2 |
| 当前成员交付扫描文件 | 126 |
| 完全重复组 | 1（人员三哈希目录中的同内容双清单，均保留） |
| 质量门禁 | 0 ERROR、4 WARNING、`PASS_WITH_WARNINGS` |
| 受控小样本独立复验 | Anti-UAV300 / DroneRF / MMAUD：均 `PASS_WITH_WARNING` |
| 官方原件交叉验证 | DroneRF L/H RAR：`PASS` |

### 对 Warning 的解释

- 质量门禁的 4 个 Warning：四个型号记录的来源许可状态尚未审阅；不是结构或文件损坏。
- 三个小样本的 Warning：`delivery_summary.json` 与实际 ZIP、`sample_manifest.json`、`SHA256.txt` 的大小/哈希不一致；实际包与后两个清单一致，仍需人员二修订摘要文件。
- `--include-fixtures` 是测试模式，包含故意不合规的 fixture，预期产生 `FAIL`，不能代表真实成员交付质量。

---

## 四、运行环境

项目使用 **`pyproject.toml` + `uv.lock`** 管理依赖。

```bash
cd data-collector
uv sync --all-groups
```

- Python：`>=3.12`
- 运行依赖：`certifi`（HTTPS CA 证书验证）
- 开发依赖：`ruff`

依赖变更：修改 `pyproject.toml` 后执行 `uv lock && uv sync --all-groups`；提交 `uv.lock`，不提交 `.venv/`。

---

## 五、运行入口

### 1. 成员交付治理重建（离线，不修改 `datasets/`）

```bash
uv run python scripts/run_all.py
```

执行：成员一/二导入、关系/冲突/看板构建、成员交付哈希和质量门禁、单元测试。

### 2. 受控样本复现与已下载原件抽检

```bash
uv run python scripts/run_data_pipeline.py
```

执行：三个受控 ZIP 的哈希/完整性/内容校验、受控 `curated` 元数据索引、已下载 DroneRF RAR 的抽取比对、治理重建。

### 3. 定向元数据采集

```bash
# 预览，不联网
uv run python scripts/collect_sources.py --target COLLECT-DRONERF-GITHUB --dry-run

# 采集公开元数据
uv run python scripts/collect_sources.py --target COLLECT-DRONERF-MENDELEY
```

支持厂商 HTTP/PDF、GitHub、Zenodo、Mendeley、FCC/FAA 人工确认结果 URL；优先使用 `ETag`/`Last-Modified`，无验证器时使用元数据 SHA-256 回退。

### 4. 已审核文件下载

```bash
uv run python scripts/download_artifacts.py \
  --target DOWNLOAD-DRONERF-RF-DATA-10000-L \
  --allow-download
```

每个下载目标须在 `configs/download_targets.json` 配置 HTTPS URL、来源 ID、预期 SHA-256、大小上限、许可、`approved: true` 和 `allow_download: true`。下载器只有在哈希匹配时才原子归档到 `data/raw/` 并生成收据。

### 5. 静态检查

```bash
uv run ruff check scripts tests
```

---

## 六、主要技术产物

```text
# Schema 与模板
schemas/
templates/

# 导入、治理、采集、下载、验收脚本
scripts/import_deliverables.py
scripts/build_governance.py
scripts/run_pipeline.py
scripts/collect_sources.py
scripts/download_artifacts.py
scripts/reproduce_samples.py
scripts/validate_downloaded_artifacts.py
scripts/publish_curated_index.py

# 哈希、质量、复现与看板
data/manifests/file_manifest.jsonl
data/manifests/file_manifest.csv
data/manifests/duplicates.json
data/delivery_manifest.json
data/reports/quality_report.md
data/reports/governance_dashboard.html
data/reports/reproduction_*.md
data/reports/download_validation_DroneRF_10000_LH.md

# 小样本和下载验证记录
data/samples/reproduction_results/
data/samples/download_validation_results/
data/receipts/downloads/
```

---

## 七、后续优先事项

1. **人员二**：修订受控样本 `delivery_summary.json` 的大小和 SHA-256；
2. **人员一/三/四**：获得并归档 FCC/FAA 官方结果 URL、型号/FCC ID/Remote ID 关联证据；
3. **人员一**：补齐说明书、当前固件和厂商条款；
4. **人员二/四**：在许可允许下扩展全量数据下载、标签统计、逐帧媒体读取、点云/雷达语义校验；
5. **人员三/四**：固化 `source_id`、`entity_id`、关系谓词和许可枚举映射，将图谱 CSV 自动导入关系层；
6. **人员四**：完善参数数值化、`curated` 版本发布、动态查询 API、Graph 和筛选看板。

---

## 八、合规与事实边界

- 不绕过认证、验证码、robots、站点访问控制或使用条款；
- FCC/FAA 仅归档人工确认的官方公开结果 URL，不自动提交查询表单；
- SHA-256 相同仅标记完全重复，不自动删除原始副本；
- 许可未知、非商业、研究限定或不可再分发应保留风险状态；
- 小样本/抽检通过不等于全量数据集、硬件同步、标定、模型效果或完整监管状态已验证；
- GitHub 在本项目中可指资料来源采集；除非另行明确要求，不执行远程 Git 操作。
