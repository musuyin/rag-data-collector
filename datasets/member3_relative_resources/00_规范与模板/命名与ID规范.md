# 命名与 ID 规范

## ID 前缀

| 类型 | 前缀 | 示例 |
|------|------|------|
| 来源 | SRC- | SRC-0001 |
| 厂商 | VND- | VND-DJI |
| 型号 | MDL- | MDL-DJI-MAVIC3 |
| 部件 | CMP- | CMP-FC-STM32 |
| 软件/固件/SDK | SFW- | SFW-DJI-SDK-V5 |
| 协议 | PRT- | PRT-MAVLINK |
| 漏洞 | VUL- | VUL-CVE-2023-1234 |
| 数据集 | DST- | DST-ANTIUAV |
| 论文 | PAP- | PAP-2021-DRONERF |
| 开源项目 | OSS- | OSS-ARDUPILOT |
| 关系边 | EDG- | EDG-0001 |
| 冲突 | CNF- | CNF-0001 |
| 缺口 | GAP- | GAP-0001 |

## 文件归档命名

```
raw_archive/{类别}/{source_id}_{短标题}_{YYYYMMDD}.{ext}
```

类别建议：`vendor` / `regulator` / `paper` / `dataset_meta` / `advisory` / `opensource` / `other`

示例：`raw_archive/advisory/SRC-0012_DJI_security_notice_20240301.pdf`

## 哈希

- 算法：SHA-256
- 清单字段：`source_id, file_path, sha256, size_bytes, recorded_at`

## 关系边类型（固定词表）

- `manufactures`：厂商 → 型号
- `uses_component`：型号 → 部件
- `runs_software`：型号 → 软件/固件
- `implements_protocol`：型号/软件 → 协议
- `affected_by`：型号/软件 → 漏洞
- `documented_in`：任意实体 → 来源
- `dataset_covers`：数据集 → 型号/场景
- `depends_on`：软件 → 软件/协议
- `supplied_by`：部件 → 厂商（供应链）
- `conflicts_with`：来源A ↔ 来源B（字段冲突时）
