# 数据卡草稿：Anti-UAV（draft_by_person3）

> 状态：临时草稿，待人员二用官方小样本验证后升为正式数据卡。  
> 起草日期：2026-09-29 | 依据：SRC-0015 / SRC-0018 / SRC-0024

## 基本信息

| 字段 | 内容 |
|------|------|
| dataset_id | DST-ANTIUAV |
| 名称 | Anti-UAV（含 300 / 410 / 600 等版本） |
| 权威入口 | https://github.com/ZhaoJ9014/Anti-UAV |
| 挑战站 | https://anti-uav.github.io/ |
| Zenodo（第4届） | https://zenodo.org/records/15103888（Restricted） |
| 论文 | Anti-UAV410: IEEE TPAMI, DOI 10.1109/TPAMI.2023.3335338 |

## 模态与内容（公开描述）

- 红外（IR）视频为主；Anti-UAV300 含 RGB+IR
- 任务：反无检测/跟踪
- 标签：边界框等（410：410 视频，>438K boxes，公开论文描述）

## 许可

| 资源 | 许可 | 风险 |
|------|------|------|
| 项目代码 | MIT（仓库声明） | 中：代码与数据许可可能分离 |
| Zenodo 全量 | Restricted | 高：未授权不镜像 |

## 采集/规模（待人员二核实）

- 规模/格式/目录树：见 GitHub README 下载表
- 关键参数：未知（草稿）

## 覆盖机型

- 公开材料多为“无人机目标”通用场景；**具体型号清单待数据卡确认**（关联边暂 medium）

## 小样本建议

先 README + 许可页；再 Anti-UAV300 子集。不要先下 Zenodo Restricted 全量。

## 人员二核对清单

- [ ] 权威下载 URL 最终拍板  
- [ ] 数据许可原文粘贴  
- [ ] 覆盖机型列表  
- [ ] 小样本哈希  
