# 数据卡草稿：MMAUD（draft_by_person3）

> 状态：临时草稿，待人员二小样本验证。  
> 起草日期：2026-09-29 | 依据：SRC-0017 / SRC-0026

## 基本信息

| 字段 | 内容 |
|------|------|
| dataset_id | DST-MMAUD |
| 名称 | MMAUD |
| 项目页 | https://ntu-aris.github.io/MMAUD/ |
| GitHub | https://github.com/ntu-aris/MMAUD |
| 预印本 | arXiv:2402.03706 |

## 模态与内容（公开描述）

- 立体视觉、多种 LiDAR、Radar、音频阵列等
- 任务：检测、分类、跟踪、轨迹估计
- 格式：rosbag / zip / ground truth（见下载表）
- 注意：rosbag 可能经 compress，播放前需 decompress

## 许可

**CC BY-NC-SA 4.0**  
- 默认：**非商业**学术  
- 商业：联系 aris.eee.ntu@gmail.com  
- ShareAlike 义务需遵守

## 项目页已列机型（关联已建）

- DJI Mavic 2 / Mavic 3 / Phantom 4 / Avata / Matrice 300（M300）

## 小样本建议

先下体积较小的一条序列元数据或短包；确认可读后再考虑全量。

## 人员二核对清单

- [ ] 确认 OneDrive 链接可用性  
- [ ] 许可是否允许课程知识库二次托管  
- [ ] 小样本哈希与传感器参数  
