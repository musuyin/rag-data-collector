# Validate Person3 CSVs by header sniffing (ASCII-only script body)
$Root = Split-Path $PSScriptRoot -Parent
$errors = New-Object System.Collections.Generic.List[string]
$allCsv = Get-ChildItem -Path $Root -Recurse -File -Filter *.csv |
    Where-Object { $_.FullName -notmatch '\\00_' -and $_.Name -ne 'hash_manifest.csv' }

function Norm-Header($h) {
    if (-not $h) { return "" }
    return (($h -replace '"','') -replace '\s','').ToLower()
}
function By-Header($prefix) {
    $p = Norm-Header $prefix
    foreach ($f in $allCsv) {
        $h = Norm-Header (Get-Content -Path $f.FullName -TotalCount 1 -ErrorAction SilentlyContinue)
        if ($h.StartsWith($p)) { return $f }
    }
    return $null
}

function Check($file, $label, $requiredCols, $idCol, $idPrefix) {
    if (-not $file) { $errors.Add("MISSING: $label"); return $null }
    $rows = Import-Csv -Path $file.FullName
    Write-Host ("OK {0} ({1}): {2} rows" -f $label, $file.Name, $rows.Count)
    if ($rows.Count -eq 0) { $errors.Add("EMPTY: $label"); return $rows }
    $cols = @($rows[0].PSObject.Properties.Name)
    foreach ($c in $requiredCols) {
        if ($cols -notcontains $c) { $errors.Add("$label missing column: $c") }
    }
    if ($idCol) {
        $i = 0
        foreach ($r in $rows) {
            $i++
            $val = [string]$r.$idCol
            if ([string]::IsNullOrWhiteSpace($val)) { $errors.Add("$label row $i empty $idCol"); continue }
            if ($idPrefix -and ($val -notlike "$idPrefix*")) { $errors.Add("$label row $i bad prefix: $val") }
        }
    }
    return $rows
}

$sources = Check (By-Header "source_id,") "source_table" @("source_id","title","url_or_path","status") "source_id" "SRC-"
$entities = Check (By-Header "entity_id,") "entity_table" @("entity_id","entity_type","name") "entity_id" $null
$relEdges = Check (By-Header "edge_id,") "relation_table" @("edge_id","subject_id","predicate","object_id") "edge_id" "EDG-"
$nodes = Check (By-Header "id,label,type") "nodes" @("id","label","type") "id" $null
$edgeFile = By-Header "id,source,target"
$gEdges = Check $edgeFile "graph_edges" @("id","source","target","type") "id" "EDG-"

$entIds = @{}
$srcIds = @{}
if ($entities) { foreach ($r in $entities) { $entIds[$r.entity_id] = $true } }
if ($sources) { foreach ($r in $sources) { $srcIds[$r.source_id] = $true } }
if ($relEdges) {
    foreach ($e in $relEdges) {
        if (-not $entIds.ContainsKey($e.subject_id) -and -not $srcIds.ContainsKey($e.subject_id)) {
            $errors.Add("dangling subject: $($e.edge_id) $($e.subject_id)")
        }
        if (-not $entIds.ContainsKey($e.object_id) -and -not $srcIds.ContainsKey($e.object_id)) {
            $errors.Add("dangling object: $($e.edge_id) $($e.object_id)")
        }
    }
}

$outDir = Join-Path $Root "08_图谱关系导出"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
$report = Join-Path $outDir "graph_selfcheck_report.txt"
$orphans = @()
if ($entities -and $relEdges) {
    $used = @{}
    foreach ($e in $relEdges) { $used[$e.subject_id] = $true; $used[$e.object_id] = $true }
    foreach ($r in $entities) { if (-not $used.ContainsKey($r.entity_id)) { $orphans += $r.entity_id } }
}
$lines = @(
    "graph self-check $(Get-Date -Format yyyy-MM-dd)",
    "entities=$($entities.Count) relation_edges=$($relEdges.Count) sources=$($sources.Count)",
    "graph_nodes=$($nodes.Count) graph_edges=$($gEdges.Count)",
    "orphan_entities_count=$($orphans.Count)",
    ($orphans -join ", ")
)
Set-Content -Path $report -Value $lines -Encoding UTF8
Write-Host ("Wrote {0}" -f $report)

if ($errors.Count -eq 0) { Write-Host "VALIDATION PASSED"; exit 0 }
Write-Host "VALIDATION FAILED:"
$errors | ForEach-Object { Write-Host (" - " + $_) }
exit 1
