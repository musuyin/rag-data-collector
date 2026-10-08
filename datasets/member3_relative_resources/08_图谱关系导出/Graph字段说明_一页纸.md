# Graph 字段说明（一页纸）

给展示系统 / 人员四联调。更新日期：2026-09-29。

## 交付文件

| 文件 | 用途 |
|------|------|
| `nodes.csv` | 全量节点 |
| `edges.csv` | 全量边（含 medium/low） |
| `edges_public.csv` | **对外展示**：仅 `confidence=high`，且 notes 不含 `supporting` / `deprecated` |
| `edges_public_README.txt` | 上次导出规则与条数 |

复现：`powershell -File export_edges_public.ps1`

## nodes.csv

| 字段 | 含义 | 示例 |
|------|------|------|
| id | 实体 ID（全局唯一） | `MDL-DJI-MAVIC3` |
| label | 展示名 | `DJI Mavic 3` |
| type | 节点类型 | vendor / model / component / software / protocol / vulnerability / dataset / paper / opensource |
| aliases | 别名，分号分隔 | `大疆;SZ DJI...` |
| status | 生命周期 | 一般为 `active` |

ID 前缀：`VND-` `MDL-` `CMP-` `SFW-` `PRT-` `VUL-` `DST-` `PAP-` `OSS-`

## edges.csv / edges_public.csv

| 字段 | 含义 | 示例 |
|------|------|------|
| id | 边 ID | `EDG-0001` |
| source | 起点实体 ID | `VND-DJI` |
| target | 终点实体 ID | `MDL-DJI-MAVIC3` |
| type | 关系谓词（固定词表） | `manufactures` |
| evidence_source_id | 证据来源 | `SRC-0001` |
| confidence | high / medium / low | `high` |
| notes | 备注；含 supporting/deprecated 时不进 public | （可空） |

### 谓词词表

`manufactures` · `uses_component` · `runs_software` · `implements_protocol` · `affected_by` · `documented_in` · `dataset_covers` · `depends_on` · `supplied_by` · `conflicts_with`

展示默认只渲染 `edges_public`；内部排查用全量 `edges.csv`。

## 与来源表对齐

- 点开边时可用 `evidence_source_id` 查 `01_来源总表/来源总表.csv`
- 本地证据文件 + SHA-256 见 `05_归档与哈希/哈希清单.csv`
- 缺口 / 许可风险见 `07_缺口许可进度/`

## 当前规模（约）

实体 **61** · 全量边 **76** · public 边 **59** · 悬空实体 **0** · 校验以 `graph_selfcheck_report.txt` / `validate_csvs.ps1` 为准。
