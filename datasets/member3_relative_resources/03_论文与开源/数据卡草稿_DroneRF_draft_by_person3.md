# 数据卡草稿：DroneRF（draft_by_person3）

> 状态：临时草稿，待人员二小样本验证。  
> 起草日期：2026-09-29 | 依据：SRC-0016 / SRC-0025

## 基本信息

| 字段 | 内容 |
|------|------|
| dataset_id | DST-DRONERF |
| 名称 | DroneRF |
| 权威入口 | https://data.mendeley.com/datasets/f4c2b4n755/1 |
| DOI | 10.17632/f4c2b4n755.1 |
| 代码页 | https://al-sad.github.io/DroneRF/ |
| 数据论文 | Data in Brief 2019, DOI 10.1016/j.dib.2019.104313 |

## 模态与内容

- 射频（RF）原始记录
- 约 227 segments；3 种无人机 + 背景
- 模式：off / on+connected / hovering / flying / video recording
- 采集：双 NI-USRP2943R，覆盖 2.4GHz（高低半带拼接）

## 许可

**CC BY 4.0** — 可署名后学术使用与再分发（保留 DOI 引用）

## 小样本建议（优先做）

下载 1 对 `*L*` + `*H*` segment，记录体积、可读性、SHA-256。

## 关联

- `dataset_covers` → CMP-RF-2G4（类型级，high）

## 人员二核对清单

- [ ] 确认 Mendeley 文件列表与体积  
- [ ] 小样本哈希回填  
- [ ] 三机型具体型号名（若论文有）  
