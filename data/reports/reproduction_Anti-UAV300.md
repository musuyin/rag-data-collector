# Controlled sample reproduction — Anti-UAV300

- Checked at: `2026-10-08T05:23:49Z`
- Result: **PASS_WITH_WARNING**
- Package: `datasets/member2_controlled_samples/packages/Anti-UAV300_rgb_ir_sequence_val_20190926_200510_1_8.zip`
- Package SHA-256: `f4c581bd626ade47b8a52fc56cd417a7186258cfbf00c64ab211a0da0b8f8f4a`

## Package checks
- size_matches_manifest: `True`
- sha256_matches_manifest: `True`
- zip_integrity: `True`
- manifest_consistency: `CONFLICT`

## Content checks
```json
{
  "required_files_present": true,
  "annotation_json_parseable": true,
  "annotation_frame_counts": [
    493,
    493
  ],
  "annotation_frame_counts_match": true,
  "frame_pairing_basis": "same controlled sequence directory and equal annotation frame counts; hardware synchronization not inferred from container metadata"
}
```

## Boundaries
- The source package in `datasets/` was not modified; extraction is regenerated in `data/staging/`.
- MP4 validation is structural in this environment (no ffprobe/OpenCV installed); it is not a full frame decode.
- Dataset-level claims are limited to this controlled sample and its declared association rule.
