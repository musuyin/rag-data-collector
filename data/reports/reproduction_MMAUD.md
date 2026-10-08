# Controlled sample reproduction — MMAUD

- Checked at: `2026-10-08T05:23:52Z`
- Result: **PASS_WITH_WARNING**
- Package: `datasets/member2_controlled_samples/packages/MMAUD_UG2_val_seq0001_camera_lidar_radar_sample.zip`
- Package SHA-256: `a1c87e498a55eb650d6a24f251a11663a3bc09b03db99029bd3bec8271c3eaad`

## Package checks
- size_matches_manifest: `True`
- sha256_matches_manifest: `True`
- zip_integrity: `True`
- manifest_consistency: `CONFLICT`

## Content checks
```json
{
  "modalities_present": [
    "Image",
    "lidar_360",
    "livox_avia",
    "radar_enhance_pcl"
  ],
  "timestamp_deltas_ms_from_camera": {
    "lidar_360": 5.788,
    "livox_avia": 8.224,
    "radar_enhance_pcl": 4.836
  },
  "association_basis": "seq0001 plus nearest filename timestamp; no calibration or hardware synchronization claim"
}
```

## Boundaries
- The source package in `datasets/` was not modified; extraction is regenerated in `data/staging/`.
- MP4 validation is structural in this environment (no ffprobe/OpenCV installed); it is not a full frame decode.
- Dataset-level claims are limited to this controlled sample and its declared association rule.
