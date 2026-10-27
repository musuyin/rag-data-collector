# 数据集模态比例：仅元数据模式

报告：[HTML](../data/reports/dataset_modality_report.html)；机器可读结果：[JSON](../data/normalized/dataset_modality_summary.json)。

本次不下载原始图片、音频、视频、信号或 ROS bag，不依赖实验室服务器登录。HTML 可离线打开，无外部图表库、CDN 或网络请求。

## 重建

```powershell
uv run python scripts/collect_sources.py --target COLLECT-MMAUD-HF-INVENTORY --target COLLECT-DRONERF-MENDELEY
# 可选：仅尝试 ZIP 的 HTTP Range 目录请求；站点拒绝 Range 时直接失败，不读取完整正文
uv run python scripts/collect_sources.py --target COLLECT-ANTI-UAV300-ZIP-DIRECTORY
uv run python scripts/build_modality_report.py
```

`--refresh` 可在分类算法改变后忽略 HTTP 条件缓存，重算公开元数据。默认仅执行显式目标，不启用任何原始载荷下载。已将采集尝试记录到 `data/collection_attempts/`，保留失败与检查时间；`data/collection_metadata/` 保存成功的轻量汇总。上游交付 `datasets/` 保持只读。

## 来源、口径与限制

- **MMAUD**：从[官方项目页](https://ntu-aris.github.io/MMAUD/)跳转到[官方链接的 Hugging Face 发布仓库](https://huggingface.co/datasets/Yuan-Shenghai/MMAUD)。读取公开 API `?blobs=true` 文件清单（本次响应约 19.8 MB），记录响应 SHA-256、发布 revision、逻辑/物理文件数、分类计数与大小；不保存整份大清单到 Git。API 响应绑定 revision，报告链接指向固定版本目录。SHA-256 是元数据响应哈希，不是本次下载复验的数据哈希。
- MMAUD 全目录统计约 367.86 GB；拆分为 3 份的 `m3e.bag` 合计为 1 个逻辑录制。全目录同时包含 bag 和已展开表示，属于存储视图，不是去重后的样本数。另提供 `V1/filesystem_format` + `V2_V3/audio` 已展开视图；该视图不能代表全部版本的解码内容。bag 中各模态比例保持 UNKNOWN。
- **Anti-UAV300**：官方页支持 RGB/IR 双模态声明，但不提供逐文件大小。本次公开 Drive 端点返回 HTTP 200，元数据读取器拒绝完整正文，没有处理登录、配额或确认页。图中的 639 JSON、636 MP4、1 Python 来自已有成员的 2026-09-29 全包验收记录，并明确标为历史证据；不是本次在线复验。分类字节数未知，大小饼图不可用。成员记录的 318 组序列与产品名 300 不一致，保留实际记录，不按名称推算数量。
- **DroneRF**：官方 Mendeley v1 API 的 23 个发布包，共约 4.027 GB 压缩存储。根据官方说明归类为射频信号；100% 表示发布包类型，不是本次解包或 CSV 数值验证。已有 API 快照经本次条件请求/内容哈希核对未变化，保留原采集时间与最新检查时间。

按文件数与按字节的分母分别为当前视图全部文件数及大小；一个视频不拆为帧，一段 RF 信号不拆为采样点。JSON 标注和校准不算自然语言文档；哈希清单归入结构化元数据。NPY 根据发布路径区分 LiDAR、Radar 和真值，不依据扩展名猜测内容。

## 访问约定审阅（2026-10-27）

- Hugging Face 使用[公开 Hub API](https://huggingface.co/docs/hub/api)，本次不需要认证；[robots](https://huggingface.co/robots.txt) 为 `Allow: /`。已查看[平台条款](https://huggingface.co/terms-of-service)，发布数据许可为 CC BY-NC-SA 4.0，不推断为商业可用。
- Google Drive 仅访问官方仓库链接的公开文件端点，已查看[服务附加条款](https://www.google.com/drive/terms-of-service/)。robots 地址通过网页工具未能读取，因此不进行目录爬取。单次 ZIP 元数据访问失败即停止，不绕过限制；重试须仍遵循同一元数据上限。
- Mendeley 使用既有官方公开数据集 API 采集器；数据集页标示 CC BY 4.0。Anti-UAV 代码 MIT 不等于数据集许可，报表继续保留数据集级许可未知。

## 验证

```powershell
uv run ruff check scripts tests
uv run python -m unittest discover -s tests -v
uv run python scripts/run_all.py
```

测试覆盖模态语义、分片逻辑计数、未知大小、HTTP 200 不读正文、ZIP 目录限量读取及分类计数守恒。报告不声称进行了原始载荷或科学内容验收。
