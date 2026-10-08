# 续报：edges_public + Autel/Parrot CVE（2026-09-29）

## edges_public.csv

- 路径：`08_图谱关系导出/edges_public.csv`
- 规则：`confidence=high` 且 notes 不含 `supporting` / `deprecated`
- 数量：**49 / 66**
- 脚本：`export_edges_public.ps1`（已修：跳过 `00_` 模板；可用脚本复现）

## Autel / Parrot 安全公告

| ADV | CVE | 对象 | 要点 |
|-----|-----|------|------|
| ADV-0007 | CVE-2023-47335 | Autel EVO Nano FW 1.6.5 | NFZ/权限相关 |
| ADV-0008 | CVE-2023-50121 | Autel EVO Nano FW 1.6.5 | 飞控 DoS |
| ADV-0009 | CVE-2024-33844 | Parrot ANAFI USA 1.10.4 | MAVLink mission type 校验 |

新增实体：`MDL-AUTEL-EVONANO`、`SFW-AUTEL-FW-GENERIC`、`SFW-PARROT-FW-GENERIC` 及对应 VUL。  
历史 ANAFI CVE-2019-3944/3945 记入 SRC-0048，未展开 PoC。

仅做关联登记，不存利用步骤。
