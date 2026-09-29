# Controlled sample reproduction — DroneRF

- Checked at: `2026-09-29T09:37:44Z`
- Result: **PASS_WITH_WARNING**
- Package: `datasets/member2_controlled_samples/packages/DroneRF_parrot_bebop_on_lh_pair_segment0.zip`
- Package SHA-256: `e45ce74c5bda4bcef51dbf9a7ae523bc016411048c237c95b183234c5657405e`

## Package checks
- size_matches_manifest: `True`
- sha256_matches_manifest: `True`
- zip_integrity: `True`
- manifest_consistency: `CONFLICT`

## Content checks
```json
{
  "l_h_files_present": true,
  "csv_physical_rows": {
    "10000L_0.csv": 1,
    "10000H_0.csv": 1
  },
  "csv_columns": {
    "10000L_0.csv": 10000000,
    "10000H_0.csv": 10000000
  },
  "csv_header_present": {
    "10000L_0.csv": false,
    "10000H_0.csv": false
  },
  "csv_numeric_preview": {
    "10000L_0.csv": [
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000"
    ],
    "10000H_0.csv": [
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000",
      "0.000000"
    ]
  },
  "filename_association": "BUI 10000 / segment 0 / L-H pair as supplied in member-two manifest"
}
```

## Boundaries
- The source package in `datasets/` was not modified; extraction is regenerated in `data/staging/`.
- MP4 validation is structural in this environment (no ffprobe/OpenCV installed); it is not a full frame decode.
- Dataset-level claims are limited to this controlled sample and its declared association rule.
