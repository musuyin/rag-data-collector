# 多模态检索平台：Schema、Data-Juicer 接入与关系检索评估

日期：2026-10-27（Asia/Shanghai）

性质：基于当前仓库代码与官方文档的架构评估；下文明确区分已实现功能和建议设计。

配套：[HTML 阅读版](retrieval_platform_architecture_assessment.html) · [数据模态比例报表](../../data/reports/dataset_modality_report.html)

## 1. 结论：方向可行，但有四个前提不能省略

**“清洗后的多模态数据 → 切片与向量索引 → 找到候选起点 → 实体对齐 → 按关系扩展 → 返回数据 batch”可行。当前项目具备元数据治理和本地存储基础，尚未实现这一检索闭环。**

最需要修正的不是流程顺序，而是以下四个假设：

1. **现有 Schema 不是三个数据集原始载荷的统一标准化协议。** 它主要管理型号资料、数据集卡、治理关系及通用入库元数据；不能直接约束一张图片、一个 ROS topic 或一段 RF 波形。
2. **图片相似不能直接证明“同一架无人机”。** 普通视觉向量可以召回相似图像或型号候选；个体身份需要编号、数据集目标 ID、跟踪轨迹或其他足够证据。系统必须允许“不知道是哪一架”。
3. **三个数据集之间不天然存在个体级连接。** 同型号、同名或相近外观不能证明是同一架、同一次飞行或同一时间的传感器观测。
4. **三跳是查询预算，不是相关性或完整性的保证。** 起点识别、边的质量、关系路径、索引覆盖和数据访问权限共同决定能找回什么。

| 当前理解 | 判断 | 更准确的说法 |
|---|---|---|
| 让同伴按现有 Schema 处理即可 | 不充分 | 可以复用来源、许可、稳定 ID 等公共字段，还需定义资产、清洗输出、定位、切片和关系契约 |
| 子集跑通，整个数据集就能用同一逻辑 | 有条件成立 | 仅当同版本、同格式、同语义的对象均被该处理配置覆盖；全量仍需扫描、分批校验和异常隔离 |
| Data-Juicer 清洗后，我们负责切片向量化 | 可以这样分工 | 同时约定谁解码 ROS bag、谁保留标注与时间映射、谁产生处理审计和关系证据 |
| 应对原始数据建边，而不是对向量建边 | 大方向正确 | 业务边连接实体、原始资产和可追溯派生内容；向量是可替换的检索表示 |
| 输入图片，直接匹配无人机元数据节点 | 不一定 | 通常先命中某张图片、视频帧或 crop，再通过稳定 ID 与关系定位候选实体 |
| 三跳就能找出大部分相关数据 | 不能承诺 | 只会得到“已建图且符合当前路径策略”的可达子集，必须用标注查询评测召回率 |

## 2. 当前 Schema 到底描述了什么

### 2.1 仓库实际存在的协议

| 文件 | 当前对象与用途 | 不能据此声称已解决的内容 |
|---|---|---|
| [model_record.schema.json](../../schemas/model_record.schema.json) | 厂商、型号、参数、来源、原文摘录与定位 | 某一架实体机、图像目标 ID、逐帧观测 |
| [dataset_card.schema.json](../../schemas/dataset_card.schema.json) | 整个数据集的名称、模态、格式、规模、许可、样本验证状态 | 每个文件/窗口的有效载荷、时钟和坐标系 |
| [relation_record.schema.json](../../schemas/relation_record.schema.json) | 主语、谓语、宾语、来源及证据位置 | 完整节点注册、端点类型约束、候选/撤销生命周期和遍历服务 |
| [conflict_record.schema.json](../../schemas/conflict_record.schema.json) | 已发现的事实冲突与处理状态 | 自动完成实体消歧 |
| [ingestion_record.schema.json](../../schemas/ingestion_record.schema.json) | 本地元数据入库公共外壳 | 针对媒体、清洗结果、切片、向量和跨模态对齐的严格协议 |

[import_deliverables.py](../../scripts/import_deliverables.py) 实际读取成员一的 Excel 和成员二的三张数据卡，生成 **4 条型号记录、3 条数据集卡、36 条证据及 25 个来源登记**。它没有把三个网站上的全部图片、视频、点云和信号解析成统一媒体记录。`--clean` 表示重建生成产物，不是对信号或图像执行业务清洗。

已有 [reproduce_samples.py](../../scripts/reproduce_samples.py) 针对受控小样本做格式/哈希等检查，但不等于全量标准化流水线。当前本地受控样本包缺失，治理审计记录的是 `AUDITABLE_NOT_INDEPENDENTLY_REPRODUCED`；成员先前的验收记录与本次独立重现必须分开。

### 2.2 两个容易误判的地方

第一，通用入库 Schema 允许额外字段，`record_type` 也是开放字符串。某条记录通过校验，不代表其 `timestamp`、`bbox`、`asset_id` 或 RF 采样单位已验证。当前 [Validator](../../scripts/lancedb_app/records.py) 只对 `model`、`dataset` 额外应用对应业务 Schema；不会因 `record_type=relation` 自动加载关系 Schema。

第二，现有数据集卡的模态枚举和映射没有显式的 `lidar` 类别；导入器把未映射模态保留在 `import_metadata.unmapped_modalities`。数据集卡导入代码还将 `sample_validation_status` 固定写为 `passed`，不能据此推导“全量原始数据已通过验证”。这些是新接入协议需要纠正的语义缺口，不应在新平台继续扩大。

**可以复用现有治理字段；不能要求所有原始数据都变成一张 dataset card。**

## 3. Data-Juicer 的输出能否事先确定

### 3.1 可以确定交付契约，不能猜测同伴当前实际输出

Data-Juicer 的导出格式、字段名及保留内容由版本、执行模式、输入结构、recipe 和算子决定。官方默认模式可导出 JSONL、JSON、Parquet；Ray 模式还提供其他格式。能够导出 `.lance` 文件，也不代表自动生成了我们的检索表、业务关系、embedding 或应用审计。[官方导出文档](https://datajuicer.github.io/data-juicer/en/main/docs/Export.html)

算子的常见数据键包括 `text`、`images`、`audios`、`videos`，键名可配置；它们是处理接口，不是我们项目的业务本体。不要假设所有算子都会无损保留自定义字段，必须拿实际 recipe 做输入/输出契约检查。[算子基类](https://github.com/datajuicer/data-juicer/blob/main/data_juicer/ops/base_op.py)

当前仓库没有 Data-Juicer 依赖、recipe、同伴输出样例或适配器。因此现在能够确认的是框架支持的格式与接口约定，**尚不能确认同伴的每一行输出具体有哪些字段、哪些样本会被过滤、媒体路径会如何改变**。

### 3.2 建议双方先冻结的交付包（待实现）

```text
cleaned-delivery/
├── manifest.json          # job_id、Schema/工具版本、配置哈希、文件数量与哈希
├── assets-00001.jsonl     # 一行一个已登记的资产或派生对象
├── lineage.jsonl          # 原始对象 → 清洗输出；含拆分/合并/过滤状态
├── annotations.jsonl      # 标签、目标、时间、坐标系及变换后的定位
├── processing_events.jsonl # 每个处理单元的保留/拒绝/失败与原因
└── payloads/              # 可选；或引用服务器受控存储 URI
```

首期用 JSONL 便于检查；全量可以采用同一字段契约的 Parquet。大型媒体不装进 JSONL，也不把整段 RF 数组变成一个巨大的 JSON 行。交付路径必须是接收端能解析的受控 URI，不能只是同伴电脑上的绝对路径。

面向 Data-Juicer 图像算子的工作记录，可以约定成下面这样的结构；`metadata` 是我们主动保留的业务字段，不能假设框架会自动补齐。空 `text` 不代表生成了 caption，也不应因此套用文本长度过滤器。实际字段保留情况必须经过 recipe 测试：

```json
{
  "text": "",
  "images": ["受控存储中可解析的图片路径"],
  "metadata": {
    "asset_id": "RAW-IMAGE-EXAMPLE",
    "dataset_id": "DATASET-MMAUD",
    "sequence_id": "example-sequence"
  }
}
```

**算子工作记录与最终交付记录可以不同**：同伴的导出步骤或我们的接入适配器负责从 `images/videos/audios` 和保留下来的元数据生成统一资产记录。`asset_uri` 是我们的入库约定，不是所有 Data-Juicer 算子都直接识别的默认输入键。

建议必备信息：稳定对象 ID、数据集/版本/split、来源登记 ID、原件哈希与定位、输出哈希与 URI、模态、许可、处理配置和版本、结果状态，以及必要的时间/帧/采样/空间信息。未知参数保留 UNKNOWN，不补猜测值。

下面是**拟议交付记录示意**，不是 Data-Juicer 默认输出，也不是已经落地的新 Schema。`原件摘要` 等字样均为占位；实际交付必须填真实值。它不携带实体身份推测或向量。

```json
{
  "schema_id": "cleaned_asset",
  "schema_version": "1.0-draft",
  "record_id": "DERIVED-EXAMPLE-001",
  "record_type": "asset",
  "dataset_id": "DATASET-ANTI-UAV300",
  "dataset_version": "explicit-version-required",
  "source_id": "SRC-ANTI-UAV300-A78901B85F",
  "license_status": "unknown",
  "record_status": "draft",
  "title": "一个可追溯的视频处理输出",
  "modality": "video",
  "asset_uri": "dataset://anti-uav300/staging/example/visible.mp4",
  "payload_sha256": "实际输出的 SHA-256",
  "parents": [{
    "asset_id": "RAW-EXAMPLE-001",
    "sha256": "原件摘要",
    "locator": {"sequence_id": "example-sequence", "stream": "visible"}
  }],
  "processing": {
    "job_id": "CLEAN-EXAMPLE-001",
    "tool": "data-juicer",
    "tool_version": "双方固定的版本",
    "recipe_sha256": "实际配置摘要",
    "status": "accepted"
  }
}
```

**不能把“通用入库器容许这些额外字段”当作新契约已经实现。** 接收端需要新增严格 Schema 和语义检查，检查资产是否可读取、哈希是否匹配、父对象是否存在，以及变换后的标签能否正确落到输出内容上。

### 3.3 清洗不能丢掉可关联性

视频裁剪、抽帧或重采样会改变时间与帧号；图像 resize/crop 会改变 bbox 坐标；文本删除会改变字符偏移；RF 窗口处理会改变采样索引；去重可能合并多个来源。这些变换必须留下映射，不能保留旧标签后假装内容没变。

Data-Juicer 提供必填字段/类型等输入校验，但不能替代项目出库时的完整 JSON Schema、外键及语义验证。[数据配置与验证](https://datajuicer.github.io/data-juicer/en/main/docs/DatasetCfg.html) 其 Tracer 按算子采集有限样本，默认上限为 10，并非全量 lineage；需要另行产出完整处理事件，覆盖被过滤、失败和去重的对象。[Tracing 文档](https://datajuicer.github.io/data-juicer/en/main/docs/Tracing.html)

## 4. 子集规则如何扩展到整个数据集

**同一个 Schema 可以覆盖全量同类对象；“覆盖”必须通过检查证明，不能由子集大小或文件扩展名推断。** Schema 管字段约束，reader 管读取，recipe 管清洗，chunker 管切分，模型管 embedding；它们需要分别版本化。

| 数据 | 推荐处理配置边界 | 从已有子集直接扩展的风险 |
|---|---|---|
| MMAUD | 版本、ROS bag/topic 与已展开文件分别定义；区分相机、LiDAR、Radar、音频、真值 | UG2+ val 子集只含部分模态，不能证明所有 bag 和 V1/V2/V3 数据均可处理 |
| Anti-UAV300 | 以 sequence + stream + 时间/帧号 + annotation 定位 | 抽帧和变帧率处理可能破坏 RGB/IR 对齐，未出现目标的帧也是有效负样本 |
| DroneRF | 显式 CSV reader、BUI/段号、L/H 配对及采样索引规则 | 一行含大量数值；普通文本切片和文本质量过滤会破坏信号；未知采样率不能转成秒 |

MMAUD 官方同时提供 bag 与文件夹表示，且存在多个版本；不能把单一解压子集当成全部格式。[官方入口](https://ntu-aris.github.io/MMAUD/) DroneRF 官方说明一个段包含两部分；这支持明确的配对规则，但不足以推断与另一个数据集的图像同源或同步。[官方说明](https://data.mendeley.com/datasets/f4c2b4n755/1)

全量前先只读盘点版本、扩展名、目录、split、单位、缺失标签、损坏对象和未注册格式；对每个 profile 抽代表样本验证，然后分批导入并核对计数。数据规模放在服务器受控存储处理，本机只保留代码、轻量索引、收据和报告。

## 5. 关系应在什么时候建立

**业务关系不依赖向量化完成；也不应只连接“原始文件”。实体、资产、派生对象和切片都可以是节点。**

| 时点 | 可建立的边 | 证据与处理要求 |
|---|---|---|
| 读取原件/标注时 | 资产属于数据集、观测属于序列、L/H 配对、标注指向帧 | 来自来源清单、官方标签和可验证定位；只读保留原件 |
| 清洗产生输出时 | 派生对象 `DERIVED_FROM` 原件、重复来源映射 | 原件与输出的哈希、recipe 版本、坐标/时间映射 |
| 内容抽取与实体对齐时 | 观测 `DEPICTS` 个体、文档 `MENTIONS` 型号 | 规则或模型先提取候选，再校验实体类型与证据；不充分则 candidate |
| 切片产生时 | 切片 `PART_OF` 资产、切片提及实体、窗口观测关联 | 半开区间定位及来源映射；新增切片有新的 ID |
| 向量检索或向量化后 | 可能相似、可能同实体的候选 | 可用于发现待核验关系；相似性不能直接升级成业务事实 |

推荐离线流程是两条共享 ID 的分支：

```text
原件与官方标签（只读）
  → reader / 原件登记 / 基础结构关系
  → 标准化 → Data-Juicer 或对应模态处理 → 出库校验
        ├─ lineage + 实体抽取/对齐 + 证据审核 → 节点与业务边
        └─ 按模态切片 → chunk 定位与结构边 → embedding → LanceDB
  → 校验端点、版本、数量和引用 → 发布一个可查询快照
```

文本关系抽取可使用完整文档或带上下文的窗口，避免两个实体恰好被切片边界隔开；再把证据映射到可检索 chunk。媒体应利用原始标注和轨迹，而不是只把每张图生成一句 caption 后丢掉结构信息。

### 5.1 哪些边适合规则，哪些适合大模型

- **规则优先**：文件归属、来源、派生、帧/窗口定位、经过核验的设备 ID、数据集目标 ID、官方提供的关联。时间近邻匹配应记录时钟域、偏差和容差；若同步依据不足，保留为候选关联。
- **模型参与**：非结构化文档的实体/关系抽取、OCR、视觉型号候选或图像描述。必须记录证据、模型版本、生成方式和审核状态。
- **禁止自动当真**：相同型号就是同一架；时间戳相近就同步；同一数据集中的文件互相有关；相似向量就是同一实体。模型分数也不是经过校准的事实正确概率。

每条边至少带：端点 ID/类型、关系类型、证据对象与定位、来源、规则/模型版本、生成方式、状态、审核信息和有效版本。边需要支持 candidate、confirmed、retracted；更正时撤销旧证据，不是只不断加边。

## 6. 图片查询无人机 A：你的例子该怎样执行

### 6.1 先定义 A 指什么

| 目标层级 | 合理节点 | 能够承诺的查询范围 |
|---|---|---|
| 某型号 | DroneModel，例如某个明确型号与变体 | 与该型号有关的资料和已标注观测，不代表同一架 |
| 数据集中的目标/轨迹 | Track 或 Target，ID 带数据集版本、序列和原生目标 ID | 同一有证据的轨迹/观测集合；不自动等同于物理个体 |
| 某一架实体机 | DroneInstance，来自可信序列号或明确台账 | 经验证属于这个体的观测、飞行或文档 |
| 仅一张没有身份依据的图 | Observation / Image | 相似候选及已知关联，允许 identity unresolved |

三个公开数据集可能共享型号，但未证明共享实体机。即便知道一张图里的型号，也无法凭外观证明某个 DroneRF 录制就是这架机产生的 RF 信号。若建立 `INSTANCE_OF` 型号关系后向外走到所有同型号记录，结果应标为“型号相关”，不能展示成“这个体的全部数据”。

### 6.2 在线检索步骤

1. 接收图片；可检测/裁剪目标，处理多目标歧义，并做可用的编号/OCR 检查。
2. 使用与索引兼容的视觉编码器生成查询向量，召回 top-k 的图片、关键帧或目标 crop；保留候选及得分。确切 ID 已知时可直接走精确查询，无需先做向量搜索。
3. 从候选的 `chunk_id → asset_id → observation/track/entity_id` 找到图中的候选节点。实体节点本身不一定有向量；“一行元数据”也不天然可用图片向量检索。
4. 结合标注、身份依据、型号约束和候选差距做实体消歧；低于验收阈值时返回多个候选或 UNKNOWN。查询可以返回临时候选，不应在每次搜索时自动写入 confirmed 事实。
5. 在用户选择的范围内，沿白名单路径扩展，例如个体的观测或轨迹；型号相关资料单独标记。
6. 对候选去重、权限/许可过滤、排序和预算裁剪，返回数据项、证据路径、匹配分数、关系置信状态与截断信息。

**向量库不只用于找入口。** 它还可以在图扩展得到的几千条候选中选出与当前问题最相关的切片，或发现尚未建边的相似内容。图负责可解释的已知关联，向量负责相似/语义召回与内容排序；没有图边的对象仍可能被向量搜到，但应作为候选展示，不能冒充已确认关联。首期可以只用向量找入口，后续再增加两者交替筛选的检索策略。

LanceDB 能查询向量并返回同一行的元数据；向量编码器、查询处理和行到实体的映射仍需我们实现。[向量搜索文档](https://docs.lancedb.com/search/vector-search) 图文共享检索需要明确支持图文对齐的编码器；“维度相同”不等于同一向量空间。视觉、文本、音频、RF 和点云向量应按 embedding space/version 分开管理，跨空间结果再用明示策略融合。

**通用图片向量不是型号识别或个体重识别的验收结果；更不能直接拿图片向量与普通 RF 数组比较。** 首期可仅支持视觉召回，再由有证据的图关系取回其他模态，无需先训练全模态统一 embedding。

### 6.3 三跳扩展需要哪些限制

典型正确路径可能是：命中图片 → 已确认实体 → 某次飞行 → 对应传感器资产。也可能需要额外走“切片 → 资产”这一跳。因此 API 应说明深度从哪个种子算、哪些结构映射不计业务跳数；“三层”不是通用固定值。

若无关系约束，路径“无人机 A → 型号 → 厂商 → 该厂商全部产品”也有三跳，却包含大量无关对象。高连接度节点会让结果迅速扩大。使用带 visited 集合的 BFS/有界路径遍历，并同时限制方向、允许的关系序列、每节点扩展数、总节点/边数、查询时长和输出总大小；在入种子和每一跳都应用访问约束，避免受限中间节点泄漏。

建议默认仅使用 confirmed 且有效的业务边，候选边只在显式探索模式中出现。相似度边与事实边分离；HNSW 等索引内部的近邻边不参加业务遍历。分数衰减或重排序可控制噪声，但不是事实验证机制。

最终返回的是**可解释、可裁剪的相关数据 batch**，而不是“已经找全”的承诺。增加深度一般增加可达量，也可能增加错误；缺失的图边不会因为多走两层自动出现。

## 7. 建议的数据与接口设计（尚未实现）

### 7.1 存储分工

| 存储 | 建议内容 | 关键约束 |
|---|---|---|
| 服务器文件系统 / 对象存储 | 原始包、媒体、清洗输出、完整事件与定位映射 | 原件只增不改，按版本保留，访问受许可约束 |
| LanceDB | 按向量空间组织的 chunk、向量、定位和可筛选元数据 | 每行可回溯资产；模型更换不能原地混入旧空间 |
| 独立 SQLite 图目录（首期建议） | nodes、edges、edge_evidence、jobs、published_snapshots | 端点存在、ID 唯一、关系端点类型检查、索引与审计 |
| FastAPI | 接收任务、搜索、候选消歧、扩展和 batch 结果 | 应用层组合向量与图，不向调用者开放任意 SQL |

已有 `journal.sqlite3` 负责 LanceDB 修改审计，**不是现成的图数据库**。建议图目录另用文件/模块，保持业务职责清楚。SQLite 适合先验证单写入、低并发、小深度查询；全量性能、并发和复杂图查询超过边界后，再根据测量选择 PostgreSQL 或专用图数据库，不预设本方案能覆盖所有规模。

LanceDB 也能保存结构化边表，但仍需自行实现节点约束、遍历、版本及一致性；“把边写进一张表”不等于图服务已经完成。

### 7.2 ID、版本与发布

- 原始内容 ID 可基于完整 SHA-256；来源/获取事件另有 ID，避免相同字节丢失多个来源。
- 派生对象 ID 由父内容 ID、处理配置哈希、处理器版本及定位的规范化结构计算；chunk 再包含切分配置和边界。用规范 JSON 等无歧义编码，不直接拼接任意字符串。
- 型号/实体身份不使用媒体哈希代替；数据集原生目标 ID 必须加上数据集版本、序列等命名空间。相同型号字符串的别名/变体需有显式对齐表。
- 重切片可以替换 chunk/embedding，而经核验的实体和资产关系继续有效；仅引用旧 chunk 的证据需要重新映射或撤销。
- 多表、跨库写入不能假装存在一个原子事务。先写入不可变批次并核对引用，在单写入发布流程中记录 LanceDB 各表版本及图快照，再提交 READY 清单；查询只读明确 READY 的快照。恢复、重跑和撤销也以该版本为边界。

### 7.3 对上 API 的建议形态

以下均为新接口设计，当前 `/api/records?q=…` 并未提供这些能力：

| 拟议接口 | 作用 |
|---|---|
| `POST /api/ingestion-jobs` | 接收受控交付 manifest，校验并创建幂等任务；不接受任意远程 URL 抓取 |
| `GET /api/ingestion-jobs/{job_id}` | 查看输入覆盖、计数、失败对象、版本、收据和发布状态 |
| `POST /api/search` | 文本/图片引用等查询，返回候选、身份解析状态和可选扩展结果 |
| `POST /api/expand` | 给定可信节点，按指定路径与预算扩展 |
| `GET /api/batches/{batch_id}` | 取回同一快照的稳定结果清单和分页；原始载荷另做鉴权读取 |

扩展请求示意：

```json
{
  "seed_node_ids": ["INSTANCE-EXAMPLE"],
  "snapshot_id": "SNAPSHOT-EXAMPLE",
  "scope": "same_instance",
  "max_hops": 3,
  "allowed_relations": ["DEPICTS", "OBSERVATION_OF", "RECORDED_IN"],
  "edge_status": ["confirmed"],
  "max_nodes": 200,
  "max_edges": 500,
  "max_items": 50
}
```

关系名和白名单需在正式本体中逐一定义端点类型、方向和允许路径；示意参数不代替服务端安全上限。还应约束每节点 fanout、超时和 byte/token 预算。

返回的 batch 至少包含：`snapshot_id`、候选/确定的种子、`identity_status`、数据项 ID/类型/URI/定位、来源与许可、`match_score`、`relation_paths`、证据、`truncated` 和截断原因。相似度与边的置信度分别返回，不能混成一个“真实性分数”。大文件只返回引用；训练用 batch 还要按轨迹/个体/采集任务隔离 split，避免相邻帧泄漏到测试集。

## 8. 目前实现到哪里：以代码为准

| 能力 | 当前状态 | 证据与边界 |
|---|---|---|
| 成员交付转换与治理 | 已实现 | 4 型号、3 数据集卡、36 证据、25 来源；不是全量载荷导入 |
| 关系 JSON 生成 | 已实现基础规则 | [build_governance.py](../../scripts/build_governance.py) 生成 29 条厂商/型号/协议/模态等关系，不是跨媒体个体图谱 |
| 原件哈希、完全重复与记录门禁 | 已实现 | [run_pipeline.py](../../scripts/run_pipeline.py)；治理校验器为自定义字段检查，不等于完整媒体语义校验 |
| 受控样本复现代码 | 已有专用脚本 | 需要对应包和工具；当前本地原始小样本缺失，不能把旧成员验证当本次复现 |
| JSON/JSONL/CSV 元数据入库 | 已实现 | [import_lancedb.py](../../scripts/import_lancedb.py)；默认 7 条型号/数据集元数据，不解析 bag/视频/RF |
| LanceDB CRUD 与审计 | 已实现 | `records_v1`；SQLite 操作日志、回读、冲突保护、撤回恢复与写锁 |
| 当前搜索 API | 仅关键词/筛选 | [store.py](../../scripts/lancedb_app/store.py) 使用 SQL LIKE；没有全文索引或语义检索 |
| 向量接收与模型接入 | 未实现且明确拒收 | [records.py](../../scripts/lancedb_app/records.py) 拒绝顶层 `vector` / `embedding`；`stats.vector_search=false` |
| Data-Juicer 对接 | 未实现 | 没有 recipe、输入/输出样例、清洗交付 Schema 或接入适配器 |
| 多模态切片与向量索引 | 未实现 | 路线图中的 assets/chunks、reader/chunker 和 embedding 仍属规划 |
| 实体消歧、节点注册与多跳 API | 未实现 | 关系文件没有自动形成可查询图服务，也没有端点完整性验证闭环 |
| 三数据集构成统计 | 已实现元数据报告 | MMAUD/DroneRF 公开 API；Anti-UAV 用标明日期的历史目录，未下载原始载荷 |
| 服务器部署及全量性能 | 未验证 | 本轮 SSH 在认证前断开；未登录、未部署、未下载服务器数据 |

现有 29 条关系也不能直接当作成熟图谱导入：默认 CLI 仅扫描型号与数据集目录；关系记录缺少通用入库要求的 `license_status`，两套协议尚未打通。部分端点只是 `ORG-*`、`MODALITY-*` 等字符串而非已登记节点；带宽目前也沿用 `uses_protocol` 谓词。需要规范本体与节点，并保留原始证据，不应把现有 `reviewed` 状态直接等价为新图的 `confirmed`。

最近的 22 项本地测试验证元数据 CRUD、治理和清单统计等现有逻辑；**不构成多模态检索、个体识别、跨模态同步、三跳召回或全量性能的验证**。

## 9. 建议实施顺序与验收

### P0：先把同伴的交付变成可验收的契约

共同确认：固定的 Data-Juicer 版本与 recipe、处理对象粒度、资产/lineage/annotation/events 字段、URI 约定、哪些模态使用专用处理器、被删除/失败/合并对象如何交代。用每种支持模态的一小批真实输出做联调，自动验证字段、哈希、父子引用和定位映射；未覆盖模态明确拒收。

不要要求同伴“所有数据都按现有 dataset_card Schema 输出”。应表达为：**保留现有来源与许可治理约束，按双方新确定的 cleaned_asset 交付契约输出；这份契约仍需正式定义和实现。** Data-Juicer 对 LiDAR、RF 等对象能否直接处理，应核对实际算子；没有合适算子时可保留原件或采用专用 reader，不能假定框架自动支持。

### P1：先实现有证据的结构关系与 batch 扩展

建立节点目录和基础边；支持重复导入、版本、撤销、引用完整性和有界遍历。不依赖 LLM，先从已知 sequence/track/asset 出发返回一组可追溯数据，验证图是否真的表达了预期业务关系。

### P2：增加一个视觉召回闭环

选择一个数据集的一种受支持视觉输入；实现 reader、关键帧/crop、chunk 定位、固定视觉模型与 LanceDB 表。让查询图片召回候选，再映射到有依据的轨迹/实体并扩展。先承诺“同序列/轨迹的相关数据”或“同型号资料”，不要把没有身份标签的目标宣称为同一架实体机。

### P3：再增加语义边与跨数据集对齐

用 LLM/VLM 为非结构化证据生成候选；加入人工审核、别名与型号变体对齐。先验证型号级连接；个体级连接必须有独立身份依据。对没有共享实体的数据集，接受无法建立同个体边的结果。

### P4：在服务器上分批扩展规模

全量只读盘点 → 代表性 profile 验证 → 有界并发处理 → 幂等写入与失败恢复 → 验收后发布。先测吞吐、内存、向量维度/存储、索引额外空间、图规模、延迟和恢复时长，再决定 ANN 索引及图存储升级。网页元数据盘点仅能估算文件与空间，不能替代原始载荷的质量验证。

| 验收对象 | 需要测量什么 |
|---|---|
| 接入与恢复 | 输入对象是否都有输出或明确的过滤/失败原因；同输入同配置是否幂等；中断能否恢复 |
| 图与定位 | 已发布边端点是否完整；错误关系能否撤销；视频/图像/RF 定位在变换后是否仍正确 |
| 视觉召回 | 独立测试集的 Recall@k、误召回、未知拒识；不以几张演示图代替评测 |
| 实体对齐 | 型号、轨迹、个体分别计算正确率与误合并率；身份依据不足时应 abstain |
| 图扩展 | 标注查询的相关项精确率、召回率、路径正确性及深度增加带来的噪声 |
| batch 与权限 | 输出是否可复现；截断是否明示；权限和许可是否在种子、中间节点及载荷读取均生效 |

召回率只有在选定测试集合及相关性标注后才能测量。对未知全量语料，不应宣称“已经找到所有相关数据”。

## 10. 可直接转给同伴的协作说明

> 我们现有 Schema 主要是型号资料、数据集卡和元数据入库外壳，还不是逐文件多模态清洗协议。请先和我们对齐 cleaned_asset 交付契约，用 JSONL/Parquet 输出稳定 ID、来源/许可、原件与清洗结果的 URI/哈希、数据集版本与 split、处理配置版本、状态，以及标签和时间/坐标映射。过滤、去重和失败也需要可核对的全量记录。大型载荷放服务器受控存储。我们接收后做出库复验、按模态切片、向量化与 LanceDB 索引；原件结构关系、清洗 lineage 和官方标注关联应在前面保留，我们再补实体对齐、证据审核和图扩展。先用一批真实输出联调，之后再扩展全量。

## 11. 依据与阅读顺序

仓库实现以本报告中的代码链接为准；现有规划见 [LanceDB 路线图](../plans/lancedb_ingestion_roadmap.md)，实际运行见 [本地管理说明](../local_lancedb.md)。本报告没有修改已有 Schema 或宣称建议接口已经上线。

外部资料于 2026-10-27 核对，Data-Juicer `main` 文档代表所查文档状态，不等于同伴安装版本；联调前应锁定实际版本：

- [Data-Juicer 导出格式与统计字段](https://datajuicer.github.io/data-juicer/en/main/docs/Export.html)
- [Data-Juicer 数据配置与输入校验](https://datajuicer.github.io/data-juicer/en/main/docs/DatasetCfg.html)
- [Data-Juicer Tracing 的样本上限](https://datajuicer.github.io/data-juicer/en/main/docs/Tracing.html)
- [Data-Juicer 算子数据键](https://github.com/datajuicer/data-juicer/blob/main/data_juicer/ops/base_op.py)
- [LanceDB 向量查询](https://docs.lancedb.com/search/vector-search)
- [MMAUD 官方页面](https://ntu-aris.github.io/MMAUD/)
- [Anti-UAV 官方仓库及下载说明](https://github.com/ZhaoJ9014/Anti-UAV#data-preparation)
- [DroneRF 官方数据集说明](https://data.mendeley.com/datasets/f4c2b4n755/1)
