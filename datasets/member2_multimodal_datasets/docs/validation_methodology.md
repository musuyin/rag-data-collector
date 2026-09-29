# Validation Methodology

## Core Questions

### 1. 拿得到吗？

Source / Download Validation 关注官方来源、文件入口、远端 metadata、下载状态、hash 和 archive integrity。

### 2. 读得出来吗？

Technical Validation 关注文件是否可打开、能否列出结构、能否读取真实样本、格式/codec/shape/dtype 是否可记录。

### 3. 标签对得上吗？

Annotation / Label Validation 关注 annotation 是否能解析、字段是否明确、annotation record 是否能对应真实 frame/file/segment。

### 4. 模态连得起来吗？

Cross-Modal Validation 关注不同模态是否能通过稳定的 key 建立关联，例如 timestamp、frame_index、filename/BUI 或实体标签。

## Formal Levels

### Level 1: Source Validation

确认数据集真实存在、官方来源可靠、论文/页面/仓库/下载入口互相支持。Source Validation PASS 不等于 Dataset Verified。

### Level 2: Technical Validation

确认真实文件经过下载或样本获取，文件可打开、可读取，结构和统计结果可以复现。

### Level 3: Cross-Modal / Semantic Association Validation

确认不同模态或标签之间存在稳定、可复现、可索引的关联。只有真实数据经过技术验证后，才可以进入 VERIFIED / PARTIALLY_VERIFIED 判断。

## Cross-Modal Relationship Types

### Temporal Association

Example: MMAUD uses `sequence_id + timestamp` to associate Camera, LiDAR, and Radar.

### Frame Pairing

Example: Anti-UAV300 uses `sequence_id + frame_index` to pair RGB and Thermal IR frames.

### Semantic Entity Association

Example: DroneRF uses RF file naming, BUI, segment_id, Drone Model, and Operating Mode to connect raw RF files to semantic labels.

Different datasets do not need identical association methods. The requirement is that the association is explicit, stable, reproducible, and useful for a knowledge index.
