# 人员四个人总结报告：数据工程与质量核验

- **角色**：数据工程与质量核验
- **报告依据**：项目脚本、配置、机器生成清单、质量报告、采集状态、下载收据和小样本复现结果
- **报告日期**：2026-10-08
- **结论级别**：两条可重复流水线已实现并通过当前输入验证；外部来源和全量内容验证受 URL、许可、网络和原始材料可得性限制。

## 1. 职责回顾

人员四负责定向采集、归档与去重、质量门禁、数据卡/字段模板工程化、数据看板和按人员二小样本记录的独立复现验证。

## 2. 已实现能力

| 职责 | 实现 | 已验证结果 |
|---|---|---|
| 定向采集与增量更新 | `collect_sources.py`；支持 HTTP、GitHub、Zenodo、Mendeley、监管快照；ETag/Last-Modified 或元数据 SHA-256 回退 | GitHub DroneRF/MMAUD、Mendeley DroneRF 元数据已实际采集；Zenodo/FCC/FAA 等待正式输入 |
| 受控下载 | `download_artifacts.py`；HTTPS、双重开关、大小上限、预期 SHA-256、原子归档、下载收据 | DroneRF Mendeley v1 的 L/H RAR 两个原件已下载并验收 |
| 归档去重 | `run_pipeline.py`；SHA-256、JSONL/CSV 清单、完全重复组 | 当前成员交付扫描 126 文件、1 个完全重复组；重复为人员三哈希目录的同内容双清单，原件均保留 |
| 数据卡/模板工程化 | Schema、模板、`import_deliverables.py` | 4 型号、36 证据、3 数据集、25 来源被标准化 |
| 质量门禁 | Schema 子集、来源登记、字段/证据、许可 Warning、重复、内容格式与关联检查 | 当前真实交付 0 ERROR、4 WARNING、`PASS_WITH_WARNINGS` |
| 看板 | `build_governance.py` 生成静态 HTML 与 JSON | `governance_dashboard.html`、看板查询数据、29 条标准化关系、2 条冲突 |
| 复现验证 | `reproduce_samples.py`、`validate_downloaded_artifacts.py` | 三个受控样本复验完成；DroneRF 官方 RAR 与受控 segment 0 交叉验证 `PASS` |

## 3. 两条可重复流水线

### A. 成员交付导入与治理

```bash
uv run python scripts/run_all.py
```

处理成员原始交付，重建型号/数据集/证据、关系、冲突、哈希清单、质量报告和治理看板；不联网、不修改 `datasets/`。

### B. 真实数据验收与受控发布

```bash
uv run python scripts/run_data_pipeline.py
```

重算人员二受控小样本的包哈希，解压到 staging，执行内容/关联校验，生成复现报告、受控 curated 元数据索引，并对已下载 DroneRF 官方 RAR 做抽取比对。

## 4. 关键验收成果

### 受控小样本

- Anti-UAV300：MP4 结构与两个标注 JSON 可读，标注帧数 493/493；
- DroneRF：L/H CSV 均为无头 1×10,000,000 数值矩阵，BUI 10000 / segment 0 配对成立；
- MMAUD：PNG 与三个 NPY 可读；seq0001 的最近时间差为 5.788/8.224/4.836 ms；
- 三者均 `PASS_WITH_WARNING`，唯一共同 Warning 是成员二 `delivery_summary.json` 与实际 ZIP、`sample_manifest.json`、`SHA256.txt` 的哈希/大小冲突。

### 真实公开原件

- 下载 DroneRF Mendeley Data v1 的 `RF Data_10000_L.rar`（217,760,401 bytes）和 `RF Data_10000_H.rar`（173,545,467 bytes）；
- 两个 HTTP 200 下载的本地 SHA-256 均与官方 API 提供值一致；
- 每个 RAR 有 22 个成员；抽取的 `10000[L/H]_0.csv` 与受控样本对应文件 SHA-256 完全一致；
- 下载原件交叉验证状态：`PASS`。

## 5. 外部来源实际状态与边界

- GitHub 和 Mendeley 元数据采集成功；
- DJI 规格页在当前网络 TLS 握手超时，Autel PDF 返回 HTTP 403；系统没有绕过限制；
- Zenodo 无真实 record ID；FCC/FAA 无人工确认官方结果 URL；
- 不自动提交监管查询表单，不绕过认证、验证码、robots 或站点条款；
- `data/raw/` 保留原件，`data/curated/` 当前只发布元数据索引，不复制受限载荷。

## 6. 未完成项与建议

1. 修订受控样本 `delivery_summary.json` 后将三项从 Warning 收口；
2. 接收 FCC/FAA 官方结果 URL 与厂商 PDF，完成监管/说明书归档；
3. 取得 Zenodo record ID；
4. 增加全量包解压、逐帧媒体解码、标签统计、点云/雷达语义校验、近似重复检测；
5. 建立 `curated/` 正式版本发布、动态筛选 API、Graph 导入和看板联调；
6. 将人员三 CSV 图谱真源纳入自动导入流程。

## 7. 完成状态

人员四已完成当前可实施的工程底座、实际下载、哈希验收和受控样本复现。未完成内容主要依赖外部监管 URL、可访问厂商资料、Zenodo 标识和更大规模原始数据，不应以当前基础验收替代全量或监管级验证。
