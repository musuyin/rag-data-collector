# FCC Grant PDF — 本轮下载清单（Step 1）

目标：本机从 **FCC 官库** 落 3 份 Grant PDF，关闭 GAP-0004 的「缺官库 PDF」部分。  
日期：2026-09-29（续）

## 优先下载（先做这 3 个）

| # | FCC ID | Grantee + Product | 关联实体 | 建议存档名 | 来源 ID |
|---|--------|-------------------|----------|------------|---------|
| 1 | SS3-L2P2104 | SS3 + L2P2104 | MDL-DJI-MAVIC3（Classic） | `SRC-0049_SS3-L2P2104_Grant_20260929.pdf` | SRC-0049 |
| 2 | SS3-MT3PD22 | SS3 + MT3PD22 | MDL-DJI-MINI3 | `SRC-0050_SS3-MT3PD22_Grant_20260929.pdf` | SRC-0050 |
| 3 | 2ATQRSMODBV3S | 2ATQR + SMODBV3S | MDL-SKYDIO-X10 | `SRC-0051_2ATQRSMODBV3S_Grant_20260929.pdf` | SRC-0051 |

## 操作步骤（官库）

1. 打开 https://www.fcc.gov/oet/ea/fccid  
2. Grantee Code 填前缀（如 `SS3`），Product Code 填后缀（如 `L2P2104`）  
3. 进入 Application → Exhibits → 下载 **Grant**（公开则下；Test Report 可选）  
4. 保存到：`raw_archive/regulator/`，文件名用上表  
5. 跑 `05_归档与哈希/compute_hashes.ps1`，更新哈希清单与来源总表

备用入口：https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm

## 完成后勾选

- [ ] SRC-0049 SS3-L2P2104 Grant 已落盘 + 哈希
- [ ] SRC-0050 SS3-MT3PD22 Grant 已落盘 + 哈希
- [ ] SRC-0051 2ATQRSMODBV3S Grant 已落盘 + 哈希
- [ ] GAP-0004 notes 更新为「3 份 grant 已归档」
- [ ] 收集进度表 W40 FCC官库PDF 改为 3/3

## 若某份不可公开

在来源总表该行 `notes` 写 `grant_not_public_YYYYMMDD`，换下一候选（如 SS3-L2ES2212 / 2AG6IANAFIM3），不要用 fccid.io 镜像 PDF 充数。

## 2026-09-29 阻断结论

本机与 Cursor 浏览器均无法打开 `fcc.gov` / `apps.fcc.gov`（Access Denied）。  
已记：`raw_archive/regulator/SRC-0044b_FCC_network_block_20260929.txt`  
GAP-0004 → `blocked_network`，owner 改为人员一/人员四。  
人员三侧不阻塞：继续用候选表 + Skydio 官方 FCC 表（SRC-0039）作中等/高置信绑定。
