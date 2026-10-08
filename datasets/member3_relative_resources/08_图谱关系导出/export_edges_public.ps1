# Export public graph edges from the largest relation CSV (edge_id header)
$Root = Split-Path $PSScriptRoot -Parent
$cands = Get-ChildItem -Path $Root -Recurse -Filter *.csv | Where-Object {
    $_.FullName -notmatch '\\00_' -and
    ((Get-Content $_.FullName -TotalCount 1 -ErrorAction SilentlyContinue) -like 'edge_id,*')
}
$rel = $cands | Sort-Object Length -Descending | Select-Object -First 1
if (-not $rel) { Write-Error "relation table not found"; exit 1 }
Write-Host ("Using relation file: {0}" -f $rel.FullName)

$rows = @(Import-Csv $rel.FullName)
$public = New-Object System.Collections.Generic.List[object]
foreach ($r in $rows) {
    $notes = ([string]$r.notes).ToLower()
    if (([string]$r.confidence).Trim().ToLower() -ne 'high') { continue }
    if ($notes -match 'supporting|deprecated') { continue }
    $public.Add([pscustomobject]@{
        id = $r.edge_id
        source = $r.subject_id
        target = $r.object_id
        type = $r.predicate
        evidence_source_id = $r.evidence_source_id
        confidence = $r.confidence
        notes = $r.notes
    }) | Out-Null
}
$outDir = Join-Path $Root "08_图谱关系导出"
$out = Join-Path $outDir "edges_public.csv"
$public | Export-Csv $out -NoTypeInformation -Encoding UTF8
@"
edges_public.csv filter rules ($(Get-Date -Format yyyy-MM-dd)):
- source_file=$($rel.Name)
- confidence == high
- notes must NOT contain: supporting, deprecated
- for Graph display / external demo
count=$($public.Count) / total=$($rows.Count)
"@ | Set-Content (Join-Path $outDir "edges_public_README.txt") -Encoding UTF8
Write-Host ("Wrote {0} public edges of {1}" -f $public.Count, $rows.Count)
