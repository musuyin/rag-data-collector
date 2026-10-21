# Schema 驱动的数据治理与 LanceDB 导入路线图

- **状态**：规划稿，暂不实现
- **更新日期**：2026-10-21
- **适用范围**：大规模、多模态数据集的受控接收、治理、标准化、分块与导入
- **首个候选数据集**：DroneRF 受控样本

## 1. 当前基础

项目已经形成一套离线、可重建的数据治理与验收能力：

- 从成员交付导入型号、数据集和证据记录；
- 构建来源、关系、冲突、缺口、许可和治理看板；
- 对 `datasets/` 执行只读 SHA-256、完全重复检测和质量门禁；
- 通过官方 API 采集 GitHub、Mendeley 等来源的公开元数据；
- 对明确批准且预先登记 SHA-256、大小上限和许可的外部工件进行受控下载；
- 对 Anti-UAV300、DroneRF、MMAUD 受控样本进行独立本地复验；
- 对已下载 DroneRF 官方 RAR 的指定 segment 与受控样本进行交叉哈希验证。

截至现有 2026-10-08 生成物：

| 指标 | 结果 |
|---|---:|
| 标准化型号 | 4 |
| 型号字段证据 | 36 |
| 标准化数据集卡 | 3 |
| 工程层来源 | 25 |
| 标准化关系 | 29 |
| 冲突登记 | 2 |
| 扫描成员交付文件 | 126 |
| 质量门禁 | 0 ERROR、4 WARNING、PASS_WITH_WARNINGS |
| 受控样本复验 | 3 个 PASS_WITH_WARNING |
| DroneRF 官方原件抽检 | PASS |

现有边界也很明确：当前工程能够登记、采集、下载、校验和治理，但尚未提供通用的数据分块、标准化载荷存储、向量化或 LanceDB 导入能力。

## 2. 下一阶段产品定位

下一阶段将项目扩展为：

> 一个 Schema 驱动、批处理式的数据治理与导入中间层。每个导入任务显式选择输入 Schema、读取器、分块规则、转换版本和目标表，输出可追溯的 LanceDB 数据库、清单、收据和验收报告。

工具本身可重复使用，每个数据集导入任务可以是一次性的。不同数据集通过不同 Schema 和显式注册的处理器接入，不通过隐式格式猜测或静默回退兼容差异。

### 目标

1. 支持数百 GB 数据集的流式扫描、分块和批量导入；
2. 任意数据库记录都能追溯到原始文件、哈希和定位范围；
3. 相同输入、Schema 和转换版本产生相同的记录 ID；
4. 中断后保留已确认批次，并通过显式收据恢复；
5. Schema、字段、维度或哈希冲突时立即失败并留下错误证据；
6. 为后续多模态 embedding、相似度检索和训练数据读取提供稳定的数据层。

### 非目标

- 不将 LanceDB 当作原始文件归档系统；
- 不自动推断许可或将未知许可升级为开放许可；
- 不自动切换读取器、分块算法或 embedding 模型；
- 不跳过坏文件后假装整批导入成功；
- 不在第一版同时支持所有模态；
- 不将数百 GB 导入并入日常离线治理入口 `run_all.py`。

## 3. 推荐数据架构

```text
外部来源 / 成员交付
        │
        ▼
Raw 原始层
原件 + URL + SHA-256 + 许可 + 下载收据
只增不改，不提交 Git
        │
        ▼
Staging 处理层
解压、解析、标准化、分块、特征或 embedding
可重新生成
        │
        ▼
LanceDB 检索层
资产记录 + 分块记录 + 向量 + 原件定位
        │
        ▼
导入收据 / 验收报告 / 查询消费者
```

### 存储职责

| 层 | 主要内容 | 生命周期 | 推荐位置 |
|---|---|---|---|
| Raw | ZIP、RAR、CSV、视频、音频、图片、点云原件 | 长期、只增不改 | 本地受控盘、NAS、S3 或 MinIO |
| Staging | 解压文件、Arrow/Parquet、媒体片段、临时批次 | 可重建 | 高吞吐临时盘或对象存储 |
| LanceDB | 标准化分块、元数据、向量、原件 URI | 可重建但可直接消费 | 本地目录或受支持的对象存储 |
| Governance | Schema、manifest、receipt、报告 | 长期、轻量 | 当前 Git 仓库 |

默认不把大型视频、音频和压缩包再次完整复制进 LanceDB。LanceDB 保存结构化分块、可检索特征、向量和原始对象 URI。文本、小型 JSON、固定长度数组等是否内联，由 Schema 中的 `payload_mode` 显式决定。

## 4. 预期交付物

```text
delivery/
├── database/
│   └── dataset.lancedb/
├── manifests/
│   ├── assets.parquet
│   └── chunks.parquet
├── schemas/
│   └── dronerf_rf_v1.json
├── receipts/
│   └── import_receipt.json
└── reports/
    └── import_quality_report.md
```

建议 LanceDB 首期包含两张逻辑表：

### `assets`

每个原始对象一条记录：

```text
asset_id, dataset_id, source_id, source_uri, source_sha256,
size_bytes, media_type, license_status, schema_id, schema_version
```

### `chunks`

每个标准化窗口或片段一条记录：

```text
chunk_id, asset_id, chunk_index, locator,
offset_start, offset_end, payload_uri, payload_sha256,
transform_id, transform_version, metadata
```

向量化阶段再显式增加：

```text
embedding, embedding_model, embedding_dimension, distance_metric
```

LanceDB 不提供关系数据库式外键约束，因此验收程序必须校验每个 `chunks.asset_id` 都对应一个存在且哈希一致的 `assets` 记录。

## 5. 首个 MVP：DroneRF 受控样本

第一版只覆盖一个确定性场景：

- 输入：已经通过现有复现流程验收的 DroneRF L/H CSV；
- 读取：无表头、单物理行、数值序列；
- 分块：Schema 显式配置固定窗口和重叠长度；
- 输出：`assets` 与 `chunks` 表；
- 验收：数量、边界、哈希、确定性 ID、重复运行和回读一致性；
- 暂不实现：实际 embedding 模型、ANN 索引、视频解码和跨模态查询。

选择 DroneRF 的原因：已有受控样本、正式清单、原始哈希和官方原件交叉验证结果，适合作为新导入层的可信基线。

## 6. Schema 契约

建议新增：

```text
schemas/ingestion_job.schema.json
schemas/asset_record.schema.json
schemas/chunk_record.schema.json
configs/ingestion/dronerf_controlled_sample_v1.json
```

导入 Schema 至少明确：

- `schema_id` 与 `schema_version`；
- 输入文件匹配规则及预期媒体类型；
- 注册的 reader 名称；
- 字段类型与必填约束；
- 分块算法、窗口、重叠及尾部处理规则；
- payload 是内联还是引用；
- 目标数据库、表名和批次大小；
- 转换 ID 与版本；
- embedding 配置，若启用则模型、版本、维度和距离度量全部必填。

处理器通过显式注册表选择；未注册 reader、chunker 或 transform 直接报错。不增加自动格式探测、模型降级或忽略错误的条件分支。

## 7. 建议模块

```text
scripts/
├── plan_import.py
├── import_lancedb.py
├── validate_lancedb_import.py
└── run_ingestion.py

data/
├── manifests/ingestion/
├── receipts/ingestion/
└── reports/ingestion/
```

### `plan_import.py`

只读扫描，不创建数据库，输出文件数量、总大小、哈希、预计分块数、预计空间、Schema 和所有前置错误。

### `import_lancedb.py`

在计划通过后再次核对原件哈希，流式读取、确定性分块、批量写入，并为每个已确认批次记录收据。

### `validate_lancedb_import.py`

验证资产与分块数量、引用完整性、分块边界、重复 ID、payload 哈希、随机回读和输入覆盖范围。

### `run_ingestion.py`

串联计划、导入和验收，但不负责下载，也不并入 `run_all.py`。下载和原始保全仍由现有受控下载流程负责。

## 8. 确定性与恢复策略

建议 ID 计算契约：

```text
asset_id = SHA256(source_sha256 + schema_id + schema_version)

chunk_id = SHA256(
  asset_id + locator + transform_id + transform_version
)
```

恢复策略：

1. 每个批次成功写入后记录输入范围、记录数和结果哈希；
2. 发生错误时立即停止，不跳过失败对象；
3. 保留已确认批次和失败收据；
4. 修正问题后由操作者显式指定收据恢复；
5. 恢复前重新验证原件、Schema、转换版本和既有批次；
6. 任一条件变化则拒绝恢复，要求创建新的导入任务。

## 9. 开发里程碑

| 阶段 | 交付 | 验收门槛 |
|---|---|---|
| M0 需求契约 | 查询用例、存储边界、Schema 与 ID 规范 | 团队确认一条端到端查询目标 |
| M1 只读规划器 | `plan_import.py`、Schema 校验、空间估算 | 不写数据即可发现全部前置错误 |
| M2 小样本导入 | DroneRF reader、chunker、LanceDB writer | 相同输入两次运行产生相同记录 |
| M3 独立验收 | 引用、边界、哈希、覆盖和回读校验 | 任意 chunk 可追溯到原始 CSV 定位 |
| M4 规模验证 | 1 GB、10–20 GB、完整数据集阶梯测试 | 记录吞吐、内存、空间与失败行为 |
| M5 向量检索 | 明确的特征/embedding 模型与索引 | 检索质量和模型版本边界可解释 |
| M6 多模态扩展 | MMAUD、Anti-UAV300 及其他 Schema | 每种模态独立 reader/chunker/validator |

## 10. 质量门禁

进入下一阶段前应满足：

- 输入文件数量、大小和 SHA-256 与计划一致；
- Schema 通过 JSON Schema 校验；
- 所有 reader、chunker、transform 均为显式注册项；
- 相同输入与版本产生相同 `asset_id`、`chunk_id` 和记录数；
- 分块范围不越界，尾部处理符合 Schema；
- 所有 chunk 均存在有效 asset 引用；
- 重复执行不会静默插入重复记录；
- 任意错误产生非零退出码和失败收据；
- 导入报告明确区分 PASS、WARNING 与 FAIL；
- 未知、研究限定、非商业和不可再分发许可继续保留风险状态。

## 11. 实施前需要确认的决策

1. 第一条真实查询是按元数据过滤、训练批读取，还是相似度搜索；
2. DroneRF 的窗口长度、重叠、尾部处理及是否需要保存原始窗口；
3. 首期 LanceDB 使用本地目录还是对象存储；
4. `payload_mode` 默认选择引用还是内联；
5. 大数据受控存储的容量、备份和访问权限；
6. embedding 在 MVP 之后采用哪种模型及如何评估检索质量。

这些决策确定前，不增加生产 LanceDB 依赖，不运行全量导入，也不改变现有治理与受控下载行为。
