# Compute SHA-256 for files under ../raw_archive and write 哈希清单.csv
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Archive = Join-Path $ScriptDir "..\raw_archive"
$OutCsv = Join-Path $ScriptDir "hash_manifest.csv"
$OutCsvZh = Join-Path $ScriptDir "哈希清单.csv"

if (-not (Test-Path $Archive)) {
    Write-Error "raw_archive not found: $Archive"
    exit 1
}

$rows = New-Object System.Collections.Generic.List[object]
Get-ChildItem -Path $Archive -Recurse -File | Where-Object { $_.Name -ne '.gitkeep' } | ForEach-Object {
    $hash = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
    $src = ""
    if ($_.Name -match '^(SRC-\d+[a-z]?)') { $src = $Matches[1] }
    $full = $_.FullName
    $idx = $full.IndexOf("raw_archive")
    $rel = if ($idx -ge 0) { $full.Substring($idx) -replace '\\','/' } else { $_.Name }
    $rows.Add([pscustomobject]@{
        source_id   = $src
        file_path   = $rel
        sha256      = $hash
        size_bytes  = $_.Length
        recorded_at = (Get-Date -Format "yyyy-MM-dd")
        recorder    = "person3"
        notes       = "auto_scan"
    }) | Out-Null
}

$header = "source_id,file_path,sha256,size_bytes,recorded_at,recorder,notes"
if ($rows.Count -eq 0) {
    Set-Content -Path $OutCsv -Value $header -Encoding UTF8
    Set-Content -Path $OutCsvZh -Value $header -Encoding UTF8
    Write-Warning "No files under raw_archive"
    exit 0
}

$rows | Export-Csv -Path $OutCsv -NoTypeInformation -Encoding UTF8
Copy-Item -Force $OutCsv $OutCsvZh
Write-Host ("Wrote {0} rows to hash_manifest.csv and Chinese-named CSV" -f $rows.Count)
$rows | Format-Table source_id, size_bytes, sha256 -AutoSize
