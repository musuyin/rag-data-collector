# 成员二数据集阶段性交付简报

## 1. 工作目标

本阶段目标不是简单罗列数据集，而是完成无人机多模态数据的收集、真实性确认、技术验证和跨模态关联判断。最终固定三个核心数据集：

- MMAUD
- Anti-UAV300
- DroneRF

这些数据集覆盖了图像/视频、红外、LiDAR、Radar、RF 信号和文本标注等多种数据类型，可支撑后续多模态存储、检索、知识索引和实验系统建设。

## 2. 已收集的数据类型

| 数据集 | 已验证数据类型 | 说明 |
|---|---|---|
| MMAUD | 图像、LiDAR、Radar、文本 metadata | 验证对象为 UG2+ derived validation subset，包含 Camera PNG、LiDAR/Radar 数据和时间戳信息 |
| Anti-UAV300 | RGB 视频、红外视频、文本标注 | 官方 Anti-UAV-RGBT.zip，包含 visible.mp4、infrared.mp4、visible.json、infrared.json |
| DroneRF | RF 数值信号、文本/文件名标签 | 官方 raw RF CSV 子集，通过文件名/BUI 关联 drone model 和 operating mode |

因此，本阶段收集的数据不只是“文字”，也包括图像、视频和多种传感器数据：

- 图像：MMAUD Camera PNG
- 视频：Anti-UAV300 RGB / Thermal IR MP4
- 传感器：MMAUD LiDAR、Radar；DroneRF Raw RF
- 文本：JSON annotation、CSV numeric RF、metadata、download manifest、validation report

## 3. 验证方法

本阶段采用三层验证流程。

### 3.1 Source Validation

首先确认数据集来源是否可靠，包括：

- 官方网站、官方 GitHub、论文、官方下载入口
- 数据集名称、版本、模态、规模是否一致
- license / redistribution 风险是否明确

注意：Source Validation PASS 只代表来源可靠，不代表真实文件已经验证。

### 3.2 Technical Validation

对真实数据文件进行技术验证，包括：

- 下载文件大小是否与官方 metadata 一致
- SHA-256 hash 记录
- ZIP/RAR archive 是否可打开
- 文件是否可读取
- 图像/视频/RF/annotation 是否能被程序解析
- 文件数量、sequence 数量、格式、分辨率、FPS 等是否合理

例如：

- MMAUD：读取 Camera、LiDAR、Radar 文件结构和时间戳。
- Anti-UAV300：解码 sampled RGB/IR video frames，解析 JSON annotation。
- DroneRF：解压官方 RAR，读取 raw RF CSV，并验证 filename label 结构。

### 3.3 Cross-Modal Validation

最后判断不同模态之间能否建立稳定关联。不同数据集采用不同的对齐方式：

| 数据集 | 跨模态关联方式 | 关联强度 |
|---|---|---|
| MMAUD | sequence_id + timestamp | PARTIAL / 可用于 timestamp-level association |
| Anti-UAV300 | sequence_id + frame_index | STRONG / 318/318 sequence frame pairing |
| DroneRF | filename/BUI + segment_id + drone model + operating mode | STRONG semantic association |

## 4. 跨模态如何对齐

### 4.1 MMAUD：基于时间戳对齐

MMAUD 的 Camera、LiDAR、Radar 不是简单按帧编号对齐，而是通过：

```text
sequence_id + timestamp
```

建立跨模态关系。验证中确认不同模态文件具有可解析时间戳，可以进行 nearest-neighbor timestamp association。

当前结论：

- Camera / LiDAR / Radar 技术验证通过。
- sequence-level association 通过。
- timestamp-level association 可用。
- 但 calibration、Audio、Ground Truth 和 strict hardware synchronization 尚未完整验证。

### 4.2 Anti-UAV300：基于帧编号对齐

Anti-UAV300 的 RGB 和红外数据采用更直接的配对方式：

```text
sequence_id + frame_index
```

每个 sequence 下都有：

- visible.mp4
- infrared.mp4
- visible.json
- infrared.json

验证结果显示：

- 318 / 318 sequences 都存在 RGB + IR + annotation。
- RGB 和 IR frame count 一致。
- FPS 一致。
- annotation index 可以对应 video frame index。
- 因此可以建立稳定的 RGB -> IR frame-level pairing。

但需要注意：这只能证明 Frame Pairing，不能证明硬件级同步。

最终状态：

```text
SYNCHRONIZATION_STATUS: FRAME_PAIRED_ONLY
HARD_SYNCHRONIZATION: NOT_CONFIRMED
```

### 4.3 DroneRF：基于语义标签关联

DroneRF 不是视觉-RF 同步数据集，没有 RGB、IR、Radar、LiDAR 与 RF 的同步关系。

它的核心价值是 RF 信号与无人机语义标签之间的关联：

```text
RF filename / BUI + segment_id -> drone model + operating mode
```

例如通过文件名可以区分：

- Background
- Parrot Bebop
- ON / Connected mode
- L/H frequency-band file pair

因此 DroneRF 的跨模态意义不是 sensor-level synchronization，而是：

```text
RF signal -> Drone Entity -> Operating Mode
```

## 5. 当前成果总结

| 数据集 | 当前状态 | 主要价值 | 主要限制 |
|---|---|---|---|
| MMAUD | PARTIALLY_VERIFIED / CROSS_MODAL_READY | Camera + LiDAR + Radar timestamp-level association | 验证的是 derived subset，不是 full V1/V2/V3；Audio 未验证 |
| Anti-UAV300 | PARTIALLY_VERIFIED / CROSS_MODAL_READY | RGB-T frame-level pairing，318/318 sequence coverage | License RISK；hard synchronization 未确认 |
| DroneRF | VERIFIED / BASIC_USABLE | RF 与 drone model / operating mode 强关联 | 仅验证官方子集；不是同步视觉-RF 数据集 |

## 6. 最终结论

本阶段已经完成三个核心无人机数据集的真实数据验证，覆盖：

- 图像/视频数据
- 红外视频数据
- LiDAR / Radar 多传感器数据
- Raw RF 信号数据
- JSON / CSV / metadata 文本数据

验证结果证明，这些数据不是只停留在论文或网页描述层面，而是已经通过真实文件下载、hash、archive integrity、文件读取、annotation 解析和跨模态关联检查。

当前成果适合作为后续多模态无人机知识管理系统的数据基础，但不应夸大为：

- 完整全量数据集全部验证完成
- 硬件级同步已证明
- 所有 license 均无风险
- 已完成模型训练或 embedding 检索系统

更准确的阶段性成果定义是：

```text
Multimodal Dataset Collection
+ Technical Validation
+ Cross-Modal Association Validation
+ Dataset Readiness Assessment
```
