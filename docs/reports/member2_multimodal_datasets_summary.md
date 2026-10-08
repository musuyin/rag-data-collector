# 人员二个人总结报告：多模态数据集

- **角色**：多模态数据集
- **报告依据**：`datasets/member2_multimodal_datasets/`、`datasets/member2_controlled_samples/`、人员四独立复现和下载抽检结果
- **报告日期**：2026-10-08
- **结论级别**：数据卡、来源和成员二验证记录已交付；三份受控小样本已由人员四独立复验；全量数据集不等同于已全面验收。

## 1. 职责回顾

人员二负责收集图像、视频、红外、声音、射频、雷达、轨迹和飞行日志等多模态资料，围绕 Anti-UAV、DroneRF、MMAUD 等公开数据集检查规模、格式、标签、许可、采集环境和关键参数，并先以小样本验证可用性。

## 2. 已交付成果

交付资料位于：

```text
datasets/member2_multimodal_datasets/
datasets/member2_controlled_samples/
```

已提供的数据集资料包括数据卡、来源清单、模态覆盖、验证矩阵、验证记录和最终验证报告。人员四已将其标准化为 3 张数据集卡，并登记来源、模态、许可风险和关联规则：

```text
data/records/imported/datasets/
configs/sources/sources.json
```

| 数据集 | 已交付模态/关联规则 | 许可与可用性结论 |
|---|---|---|
| Anti-UAV300 | RGB/视频、Thermal IR；`sequence_id + frame_index` | 数据集许可仍为风险；受控内部样本，不默认再分发 |
| DroneRF | RF；BUI、工作模式、segment 和 L/H 文件名关系 | CC BY 4.0；允许署名条件下的内部存储和共享 |
| MMAUD | Camera、LiDAR、Livox、Radar、Audio/Trajectory 资料；`sequence_id + timestamp` | CC BY-NC-SA 4.0；限内部非商业研究，标定与全量验证仍有限制 |

## 3. 小样本独立复现结果

人员二提供了三个受控 ZIP 小样本。人员四在不修改 `datasets/` 原件的前提下重算包大小和 SHA-256、执行 ZIP 完整性检查，并解压到 `data/staging/controlled_samples/` 做格式和关联校验。

| 数据集 | 独立复验内容 | 状态 |
|---|---|---|
| Anti-UAV300 | ZIP 与两个一致清单匹配；visible/infrared MP4 结构存在；两个 JSON 标注可解析，帧数 493/493 | `PASS_WITH_WARNING` |
| DroneRF | ZIP 与两个一致清单匹配；L/H CSV 为无头 1×10,000,000 数值矩阵；BUI 10000、segment 0 关联成立 | `PASS_WITH_WARNING` |
| MMAUD | ZIP 与两个一致清单匹配；PNG 与 3 个 NPY 可读；相对 Camera 的 LiDAR/Livox/Radar 最近时间差为 5.788/8.224/4.836 ms | `PASS_WITH_WARNING` |

复验输出：

```text
data/samples/reproduction_results/
data/reports/reproduction_*.md
```

三个 Warning 的共同原因是：`delivery_summary.json` 中的大小和 SHA-256 与实际 ZIP、`sample_manifest.json`、`SHA256.txt` 不一致。实际 ZIP 与后两者一致，因此内容未出现损坏；但摘要文件需要人员二修订或书面确认。

## 4. 真实来源交叉验证

DroneRF 的两个 Mendeley Data v1 官方 RAR 已由人员四下载并以官方 API 哈希验收：

```text
RF Data_10000_L.rar  217,760,401 bytes
RF Data_10000_H.rar  173,545,467 bytes
```

两个文件均 HTTP 200、大小和官方 SHA-256 一致。每个 RAR 列出 22 个成员；从官方原件抽取的 `10000L_0.csv`、`10000H_0.csv` 与受控小样本中对应 CSV 的 SHA-256 完全一致，下载原件抽检结果为 `PASS`。

结果位置：

```text
data/samples/download_validation_results/DroneRF_10000_LH.json
data/reports/download_validation_DroneRF_10000_LH.md
```

## 5. 对项目的贡献

1. 提供三类不同模态和许可约束的数据集卡，支撑数据选择与风险控制；
2. 提供样本验证记录、关联键和已知限制，使复现流程有可执行的预期；
3. 用受控小样本与公开 DroneRF 原件建立了可验证链条；
4. 为人员三的图谱关系、人员四的 Schema、验收器和看板提供数据集层输入。

## 6. 当前限制与待办

- 修订 `delivery_summary.json`，使其哈希/大小与实际受控 ZIP 一致；
- Anti-UAV300：当前验证 sequence/frame 配对，不证明硬件同步、视频 PTS 传感器时间、配准或模型效果；
- MMAUD：当前仅证明指定 `seq0001` 小样本的格式和最近时间戳关系，不证明标定、硬件同步或全量数据质量；成员二旧记录还指出本地缺少标定矩阵和参考 CSV；
- 全量数据下载、完整标签统计、全量格式扫描和模型级验证尚未完成；
- 应补充每个数据集的版本冻结、样本抽样规则、标签语义说明和可再分发边界。

## 7. 完成状态

人员二已完成阶段性来源清单、数据卡、小样本包和验证记录交付；小样本已获得独立复验支持。当前结论仅覆盖受控样本和 DroneRF 指定原件抽检，不能扩展为三个完整公开数据集均已全量独立验证。
