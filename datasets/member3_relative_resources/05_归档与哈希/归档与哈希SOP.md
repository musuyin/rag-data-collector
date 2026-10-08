# 归档与哈希 SOP（人员三）

## 何时归档

来源总表中 `status` 从 `registered` / `needs_url` 变为可本地保存时：网页另存 PDF/HTML、说明书、公告原文、数据集说明页、许可证全文等。

## 步骤

1. 按命名规范放入 `raw_archive/{类别}/`
2. 计算 SHA-256，写入 `05_归档与哈希/哈希清单.csv`
3. 回来源总表补充本地路径（可在 `notes` 或后续扩展 `local_path` 列）
4. 若与已有文件哈希相同 → 记入 `06_去重与冲突/去重清单.csv`
5. 若同一字段两来源值不同 → 记入 `06_去重与冲突/冲突登记表.csv`

## Windows PowerShell 计算哈希示例

```powershell
Get-FileHash -Algorithm SHA256 ".\raw_archive\vendor\SRC-0001_xxx.pdf" | Format-List
```

批量：

```powershell
Get-ChildItem -Recurse .\raw_archive -File | Get-FileHash -Algorithm SHA256 |
  Select-Object Hash, Path | Export-Csv -NoTypeInformation .\05_归档与哈希\_scan_temp.csv
```

## 交给人员四

本目录人工清单是“真源”；人员四可用脚本重算并对比 `_scan_temp.csv` 做复现验证。
