# MMAUD Sample Validation

Dataset: MMAUD  
Sample: no complete raw sample downloaded; UG2+ Track 5 metadata/reference CSVs inspected through Drive connector preview  
Sample Source: https://drive.google.com/drive/folders/1wk-c5xVX6701WNI_In1ba3_D4LSjRYv5 and https://drive.google.com/drive/folders/1_LpPyIfETQS-k2vlSsbzI9pzyVzZScSx  
Sample Size: 0 local raw bytes; smallest discovered official raw-data package is `MMAUD_2D.zip`, 4,690,057,225 bytes.

## ACCESS

Download: FAIL

Reason:

- Google Drive connector listing/read succeeded.
- Direct shell download from `drive.google.com` and `drive.usercontent.google.com` timed out.
- Connector controlled file URLs returned `403` from `curl`.
- All discovered raw-data packages exceed the `2 GB` hard limit.

Decompression: NOT_REQUIRED

Reason:

- No archive was downloaded.

## FILES

File Count: 0 local raw files

Directory Count: 1 local sample directory (`samples/MMAUD/raw/`)

Total Size: 0 bytes

Formats:

| Extension | Count |
|---|---:|
| none | 0 |

Readable Files: PARTIAL

Connector-readable files:

| File | Size | Observed Structure |
|---|---:|---|
| `README.md` | 4,336 bytes | Markdown text documenting UG2+ data layout |
| `validation_ref_new (for your ref).csv` | 102,063 bytes | CSV preview with `Sequence`, `Timestamp`, `Position`, `Classification` |
| `test_timestamps.csv` | 171,144 bytes | CSV preview with `Sequence`, `Timestamp`, `Position`, `Classification`; `Position` and `Classification` empty in preview |

## ANNOTATION

Annotation Exists: PASS

Annotation Parse: NOT_TESTED

Annotation Correspondence: NOT_TESTED

Observed fields from `validation_ref_new (for your ref).csv` preview:

| Field | Status |
|---|---|
| `Sequence` | present |
| `Timestamp` | present |
| `Position` | present, numpy-like 3-float array string |
| `Classification` | present, integer class id |

Annotation reference check:

| Metric | Value |
|---|---:|
| checked_annotations | 0 |
| valid_references | 0 |
| missing_references | 0 |
| reference_success_rate | NOT_TESTED |

Reason:

- No image/sensor data files were downloaded, so CSV rows cannot be checked against actual frame files.

## TIMESTAMP

Timestamp Exists: PASS

Timestamp Parse: PARTIAL

Monotonic: NOT_TESTED

Synchronization: NOT_TESTED

Observed:

- CSV previews use decimal Unix epoch timestamps, for example `1706255621.564602` and `1713163087.641995`.
- README states raw files are named with `ros_timestamp`.

Not tested:

- Duplicate timestamps.
- Per-sequence monotonicity.
- Camera versus ground-truth timestamp differences.
- Any cross-modal synchronization status.

Synchronization status: NOT_TESTED

## MULTIMODAL

Modalities Found:

- README-documented fisheye `Image`
- README-documented `lidar_360`
- README-documented `livox_avia`
- README-documented `radar_enhance_pcl`
- README-documented `ground_truth`
- README-documented `class`

Common Sequence ID: SOURCE_DOCUMENTED_NOT_SAMPLE_VERIFIED

Common Timestamp: SOURCE_DOCUMENTED_NOT_SAMPLE_VERIFIED

Calibration: SOURCE_DOCUMENTED_NOT_SAMPLE_VERIFIED

Association Strength: WEAK

Reason:

- Multimodal structure is documented, but no actual files from those modality folders were downloaded.

## SOURCE AUDIT CONSISTENCY

| Source Audit Claim | Result |
|---|---|
| PNG image files | SOURCE_DOCUMENTED_NOT_FOUND_IN_LOCAL_SAMPLE |
| NPY files | SOURCE_DOCUMENTED_NOT_FOUND_IN_LOCAL_SAMPLE |
| PCD files | NOT_TESTED |
| BAG files | NOT_TESTED |
| CSV metadata/reference files | CONFIRMED_BY_CONNECTOR_PREVIEW |
| Sequence-level structure | SOURCE_DOCUMENTED_NOT_SAMPLE_VERIFIED |
| Common timestamps | SOURCE_DOCUMENTED_NOT_SAMPLE_VERIFIED |

Note: `NOT_FOUND_IN_LOCAL_SAMPLE` does not mean the official source is wrong. No raw package was downloaded.

## PROBLEMS

- `MMAUD_2D.zip` is 4,690,057,225 bytes, above the 2 GB hard limit.
- UG2+ `val.zip` is 5,325,448,505 bytes, above the 2 GB hard limit.
- UG2+ `fisheye_calibration.zip` is 7,239,409,071 bytes, above the 2 GB hard limit.
- UG2+ `train.zip` is 139,733,346,888 bytes, above the 2 GB hard limit.
- Local shell download from Google Drive timed out.
- Connector-controlled file URLs could not be materialized locally with `curl`.
- No local raw sample files exist, so image/NPY/PCD/BAG checks were not performed.
- No annotation-to-image correspondence check was possible.
- No cross-modal timestamp comparison was possible.

## FINAL RESULT

Source Validation: PASS

Technical Validation: PARTIAL

Cross-modal Validation: NOT_TESTED

Final Dataset Status: UNVERIFIED

Project Readiness: NOT_READY

## Next Decision Required

The smallest discovered official raw-data package is `MMAUD_2D.zip` at 4.69 GB. It is worth downloading only if you explicitly override the current `>2 GB` prohibition for this phase.
