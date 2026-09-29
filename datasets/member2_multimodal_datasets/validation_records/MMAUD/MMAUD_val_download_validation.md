# MMAUD val.zip Download Validation

Dataset: MMAUD

Subset: UG2+ val

Original or Derived: DERIVED_SUBSET

File: val.zip

Source: https://drive.google.com/file/d/1T7MLHfKsFYm8fjnJcn39ZrzFjHv-z-fh/view?usp=drivesdk

## Remote Metadata Check

| Field | Value |
|---|---:|
| remote_filename | val.zip |
| remote_mime_type | application/zip |
| expected_size | 5,325,448,505 bytes |
| metadata_status | PASS |

## Download

| Field | Value |
|---|---|
| download_status | PASS |
| local_path | samples/MMAUD/raw/val.zip |
| file_exists | YES |
| actual_size | 5,325,448,505 bytes |
| actual_size_gb | 5.325448505 GB |
| sha256 | D2B4424284F3673FA9296B49582D87076DB058765DB26EEB73C1A2C48CC17C9B |
| download_time | 2026-09-22T22:10:18+08:00 |

Download notes:

- Google Drive connector refused raw download because the file exceeds its 268,435,456-byte limit.
- Direct `curl` attempts timed out.
- Local browser download completed as `C:/Users/水火/Downloads/val.zip`.
- The completed browser file was copied unchanged to `samples/MMAUD/raw/val.zip`.

## ZIP

| Field | Value |
|---|---|
| ZIP Open | PASS |
| ZIP Integrity | PASS |
| Archive Entry Count Total | 5,325 |
| Archive File Count | 5,244 |
| Estimated Extracted Size | 6,419,220,734 bytes |
| Sequence Count | 16 |

ZIP notes:

- ZIP central directory opened successfully.
- `python -m zipfile -t samples/MMAUD/raw/val.zip` completed with `Done testing`.
- No archive contents were extracted or parsed.

## Structure

Top Level Structure:

- `val/`

Detected Directory Names:

- `val/seq0001/`
- `val/seq0002/`
- `val/seq0003/`
- `val/seq0004/`
- `val/seq0005/`
- `val/seq0006/`
- `val/seq0007/`
- `val/seq0008/`
- `val/seq0009/`
- `val/seq0010/`
- `val/seq0011/`
- `val/seq0012/`
- `val/seq0013/`
- `val/seq0014/`
- `val/seq0015/`
- `val/seq0016/`

Per-sequence directory pattern:

- `Image/`
- `lidar_360/`
- `livox_avia/`
- `radar_enhance_pcl/`

Detected Extensions:

- `.png`: 2,426
- `.npy`: 2,818

## Result

READY_FOR_FILE_INSPECTION

READY_FOR_FILE_INSPECTION: YES
