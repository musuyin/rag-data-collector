# 本地 LanceDB 导入与管理

状态：已实现首期元数据导入、CRUD 与本地管理页面。业务清洗、模型调用、向量化、图片预览、图文检索及 DroneRF 信号分块不在本版实现范围内。

## 快速运行

使用 Python 3.12 和 uv，在仓库根目录执行：

```powershell
uv sync --all-groups

# 只读验证现有 4 个型号与 3 张数据集卡，不创建数据库
uv run python scripts/import_lancedb.py --dry-run

# 入库；再次执行会跳过内容相同的记录
uv run python scripts/import_lancedb.py

# 启动页面：http://127.0.0.1:8000
uv run python scripts/serve_lancedb.py
```

按 Ctrl+C 停止服务。CLI 与 Web 共用同一数据目录时，只允许一个进程持有写锁；重新导入前先停止 Web 服务。页面启动时没有数据也可正常使用“新建记录”。

如果当前电脑没有全局 uv，而本次工作区保留了本地工具，可以将命令中的 `uv` 替换为 `& .\.uv-tools\bin\uv.exe`。已有环境也可直接运行 `.\.venv\Scripts\python.exe scripts/serve_lancedb.py`；依赖仍统一由 `pyproject.toml` 和 `uv.lock` 管理。

## 导入自己的数据

```powershell
uv run python scripts/import_lancedb.py --input path/to/records.jsonl --dry-run
uv run python scripts/import_lancedb.py --input path/to/records.jsonl --batch-size 100

# 另一个独立数据库；导入端和服务端必须指定相同 --home
uv run python scripts/import_lancedb.py --input path/to/records.csv --home data/local/my_dataset
uv run python scripts/serve_lancedb.py --home data/local/my_dataset --port 8001
```

`--input` 接受多个文件或目录。目录递归读取 `.json`、`.jsonl`、`.csv`；应传入专用记录目录，避免混入下载清单、报告或未转换的数据卡。仅支持标准化元数据，不会把原始 Excel、图片、视频、RF CSV 自动解释成业务记录。

- JSON：一个对象或对象数组；单文件上限 64 MiB。
- JSONL：每行一个对象；适合较大的交付。
- CSV：UTF-8（允许 BOM），第一行为非重复表头；字段默认字符串。嵌套对象和数组使用 CSV 正确转义后的 JSON 单元格；`sample_count` 使用 JSON 数值。
- 单条记录上限 2 MiB。大型载荷通过 `asset_uri` 引用，不复制原件。

记录结构见 `schemas/ingestion_record.schema.json`。最低字段如下；示意中的来源必须替换为已登记来源：

```json
{
  "record_id": "DOC-EXAMPLE-001",
  "record_type": "document",
  "title": "资料标题",
  "text": "已由上游处理的文本",
  "source_id": "替换为 configs/sources/sources.json 中的来源 ID",
  "license_status": "unknown",
  "record_status": "draft",
  "dataset_id": "可选数据集 ID",
  "asset_uri": "可选受控原件 URI"
}
```

`record_id` 由交付方给出且应稳定、唯一；不使用可变行号自动生成。`model` 和 `dataset` 记录额外通过既有型号/数据集 Schema 校验。完整业务字段保存在 `body_json`，常用字段投影为 LanceDB 列以便查询。来源 ID 必须已登记，变更来源登记后重启服务。`vector`、`embedding` 字段本版明确拒绝接收，避免把未校验的数组误当作检索能力。

入库仅说明元数据格式和读写通过，不代表上游业务清洗完成、内容事实正确、许可审核通过或可进入 `data/curated/`。

## 校验、重复和失败处理

所有输入先只读计算 SHA-256、解析与校验，并将快照写到系统临时目录的 SQLite，再分批写入 LanceDB。扫描结束后重新核对文件哈希；发现输入变化直接失败。临时快照在任务结束后清理；受限数据运行时应使用受控临时盘。

`--dry-run` 只验证输入，不打开现有数据库，不判断库内冲突，也不声称验证业务标签或资产 URI 指向的原始文件。

- 输入解析错误、未登记来源、Schema 错误或跨文件重复 ID：入库前失败，不创建业务数据库。
- 同 ID、相同内容：跳过，不增加版本。现有 `model` / `dataset` 导入器每次重建都会刷新 `import_metadata.imported_at`，比较时仅忽略这一项运行时间；保留库内原始快照和哈希，其他内容变化仍检测冲突。
- 同 ID、不同内容：默认报冲突。
- `--replace`：显式允许更新未被 Web 修改的导入记录。人工修改记录仍报冲突，防止重建覆盖修订。
- 已撤回 ID：导入报冲突，不自动恢复。
- 导入不是全任务事务；后续批次失败时保留之前已确认批次，收据标记 `FAIL` 并记录批次数。

每次修改先持久化到 SQLite 写入日志，再写 LanceDB 并逐条回读。成功后标记日志已应用。进程在中间退出时，下次打开数据库重放未完成日志；同一 ID 的重放不会新增重复行。所有公开操作在恢复完成后执行。不要绕过本应用直接修改其管理表，日志与版本保护只覆盖本应用写入。

导入收据区分 `PASS`、`PASS_WITH_WARNINGS`、`FAIL`。非 `open` 许可仍保留原状态并提示风险，绝不自动升级许可。校验前置失败输出非零退出码和错误定位；数据库写入阶段的失败另有持久化收据。

## Web 与 API

页面提供分页、按类型/许可筛选、ID/标题/正文搜索、完整 JSON 编辑、来源信息、修改历史、撤回和恢复。关键词筛选采用 SQL LIKE，`%` 与 `_` 为通配符，不是全文索引或语义检索。分页期间发生修改可能改变行顺序，批量导入建议停止服务后进行。

| 方法 | 地址 | 用途 |
|---|---|---|
| GET | `/api/stats` | 总数、有效数、撤回数 |
| GET | `/api/sources` | 已登记来源 |
| GET | `/api/records?limit=25&offset=0&q=…&record_type=…&license_status=…&source_id=…&include_deleted=false` | 列表与筛选 |
| GET | `/api/records/{record_id}` | 详情（可读取已撤回项） |
| POST | `/api/records` | 新增，正文为记录对象 |
| PUT | `/api/records/{record_id}` | 替换业务字段，正文为 `{"record": {...}, "revision": 1}` |
| DELETE | `/api/records/{record_id}` | 撤回，正文为 `{"revision": 1}` |
| POST | `/api/records/{record_id}/restore` | 恢复，正文为 `{"revision": 2}` |
| GET | `/api/records/{record_id}/history` | 版本与业务字段快照 |
| GET | `/openapi.json` | API 契约，无外部 CDN 依赖 |

写接口需要 `application/json` 和 `X-Write-Token`。先从 `/api/session` 获取当前服务实例的 `write_token`；页面自动处理。令牌用于防止其他网站诱导浏览器写入，不是用户身份认证。服务只监听 `127.0.0.1`，不提供远程部署和多用户权限，不启用 CORS。需要团队或远程访问时再单独设计认证与权限。

详情返回 `record`（业务字段）、`system`（版本、撤回、时间、哈希）、`origin`（输入文件、哈希、定位）和 `display`。修改、撤回和恢复要求提交最新 `revision`；旧版本返回 409。`record_id` 不可修改，撤回记录需先恢复才能编辑。

删除为可恢复的逻辑撤回；不会删除原件、历史版本或从磁盘安全擦除数据。默认列表排除撤回项。应用没有任意 SQL、原件下载或任意文件读取接口，也不把文件 URI 自动变成链接或执行 HTML。

## 本地存储与备份

```text
data/local/lancedb_manager/
├── database/records_v1.lance/  # LanceDB 真正存放的记录
├── journal.sqlite3            # 操作日志和版本快照
├── receipts/                  # 导入清单、数量、结果、失败记录
└── writer.lock                # 操作系统独占锁，进程退出自动释放
```

整个 `data/local/` 已加入 Git 忽略，可能含许可受限的内容、操作历史和本地引用。备份或迁移时停止服务，完整复制 `--home` 目录；仅复制 LanceDB 表会丢失审计与恢复信息。原件仍需在受控存储中单独保全。外部输入路径在可携带的收据中仅记录文件名，仓库内输入记录相对路径。

该服务不会更改 `datasets/`、`data/raw/`、既有导入产物或质量报告，也不会将数据复制到 `data/curated/`。`--home` 禁止指向这些原件/治理目录及代码配置目录。日常 `run_all.py` 不导入或操作本地业务数据库。

## 验证

```powershell
uv run ruff check scripts tests
uv run python -m unittest discover -s tests -v
uv run python scripts/run_all.py
```

回归覆盖真实 LanceDB 读写、现有 7 条记录、重复运行、源文件不变、非法输入、冲突保护、撤回恢复、版本冲突、失败收据、写入中断恢复、进程锁、SQL 值转义及 Web API。真实小样本媒体、向量模型和大规模性能需在对应功能接入时独立验收。
