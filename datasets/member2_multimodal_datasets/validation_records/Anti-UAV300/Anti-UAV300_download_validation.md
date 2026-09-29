# Anti-UAV300 Download Validation

Dataset: Anti-UAV300  
File: Anti-UAV-RGBT.zip  
Stage: DOWNLOAD + HASH + ARCHIVE INTEGRITY + DIRECTORY INSPECTION + SEQUENCE DISCOVERY + VALIDATION SAMPLE SELECTION  
Validation time: 2026-09-29T13:39:05.7684017+08:00

## Download

| Field | Value |
|---|---|
| Source | https://drive.google.com/file/d/1NPYaop35ocVTYWHOYQQHn8YHsM9jmLGr/view |
| Remote filename | Anti-UAV-RGBT.zip |
| Remote MIME type | application/zip |
| Expected size | 6,037,566,331 bytes |
| Actual size | 6,037,566,331 bytes |
| Size status | SIZE_MATCH |
| SHA256 | ed7d80bbd8ca8e01ea784c64eb0782eae8b3a1572177535c0fada9beb53fdca8 |
| Download status | PASS |
| Download method | Windows BITS with official Google Drive usercontent endpoint |

Only `Anti-UAV-RGBT.zip` was downloaded. Anti-UAV410, Anti-UAV600, and other large packages were not downloaded.

## ZIP Integrity

| Field | Value |
|---|---|
| ZIP_OPEN | PASS |
| ZIP_INTEGRITY | PASS |
| Integrity method | Python `zipfile` streamed all archive files and verified CRC without extracting to disk |
| Archive total entries | 1,598 |
| Archive file count | 1,276 |
| Archive directory count | 322 |
| Estimated extracted size | 6,720,200,225 bytes |

## Directory Structure

Observed top-level structure:

```text
framecut.py
label_new/
  test.json
  train.json
  val.json
test/
  <sequence>/
    infrared.json
    infrared.mp4
    visible.json
    visible.mp4
train/
  <sequence>/
    infrared.json
    infrared.mp4
    visible.json
    visible.mp4
val/
  <sequence>/
    infrared.json
    infrared.mp4
    visible.json
    visible.mp4
```

Detected extensions:

| Extension | Count |
|---|---:|
| .json | 639 |
| .mp4 | 636 |
| .py | 1 |

## Sequence Discovery

| Field | Value |
|---|---|
| Sequence count | 318 |
| Test sequences | 91 |
| Train sequences | 160 |
| Val sequences | 67 |
| RGB / visible structure | FOUND: `visible.mp4` |
| IR / infrared structure | FOUND: `infrared.mp4` |
| Annotation structure | FOUND: per-sequence `visible.json` and `infrared.json`; split files under `label_new/` |

The discovered sequence count is 318, matching the official RGB-T video-pair scale. This is a directory-level discovery result, not a full per-frame validation.

## Selected Validation Sequences

Selected for the next step because each contains RGB, IR, and annotation files:

| Split | Sequence | Path |
|---|---|---|
| test | 20190925_111757_1_1 | test/20190925_111757_1_1/ |
| test | 20190926_111509_1_7 | test/20190926_111509_1_7/ |
| train | 20190925_205804_1_7 | train/20190925_205804_1_7/ |
| train | 20190926_193515_1_6 | train/20190926_193515_1_6/ |
| val | 20190926_200510_1_8 | val/20190926_200510_1_8/ |

## Scope

This step did not read all RGB frames, IR frames, or annotation contents. It did not perform RGB-IR frame matching, tracking model execution, or any downstream analysis.

LICENSE_STATUS remains `RISK`. Raw Anti-UAV300 data is retained for internal research/validation only and must not be redistributed unless redistribution rights are explicitly confirmed.

READY_FOR_RGB_IR_FILE_INSPECTION: YES
