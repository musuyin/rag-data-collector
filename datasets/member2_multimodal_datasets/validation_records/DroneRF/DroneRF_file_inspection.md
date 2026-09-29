# DroneRF RF File Inspection

Dataset: DroneRF  
Version: Mendeley Data v1  
Stage: STEP 4 - RF FILE TECHNICAL VALIDATION  
Validation time: 2026-09-29T00:04:48.2864701+08:00

## 1. Sample Overview

The inspected sample is the manually approved DroneRF validation subset:

| Role | Archive | Extracted CSVs | Segment IDs |
|---|---|---:|---|
| BACKGROUND_L | RF Data_00000_L2.rar | 20 | 21-40 |
| BACKGROUND_H | FR Data_00000_H2.rar | 20 | 21-40 |
| DRONE_L | RF Data_10000_L.rar | 21 | 0-20 |
| DRONE_H | RF Data_10000_H.rar | 21 | 0-20 |

No additional DroneRF files were downloaded.

## 2. Extraction

Extraction status: PASS  
Destination: `samples/DroneRF/extracted/`  
Extracted file count: 82  
Total extracted size: 7,816,289,911 bytes  
CSV count: 82  
Expected CSV count from archive inspection: 82  
Empty file count: 0  
Unreadable file-stream count: 0  
Unexpected extension count: 0  
Raw RAR archives modified: NO

## 3. File Structure

The extracted files preserve the archive directory names:

| Directory | CSV pattern | Count |
|---|---|---:|
| RF Data_00000_L2 | 00000L_<segment_id>.csv | 20 |
| FR Data_00000_H2 | 00000H_<segment_id>.csv | 20 |
| RF Data_10000_L | 10000L_<segment_id>.csv | 21 |
| RF Data_10000_H | 10000H_<segment_id>.csv | 21 |

## 4. L/H Pair Structure

BACKGROUND_L_H_PAIRING: PASS  
Background L and H both contain segment IDs 21-40.

DRONE_L_H_PAIRING: PASS  
Drone L and H both contain segment IDs 0-20.

PAIR_STRUCTURE_COMPATIBLE: YES for all sampled L/H pairs.

## 5. CSV Parsing

Sampled CSVs:

| Class | Segments | Files |
|---|---|---:|
| Background | 21, 30, 40 | L + H for each segment |
| Drone | 0, 10, 20 | L + H for each segment |

CSV_READABILITY: PASS  
Sampled CSV count: 12  
Delimiter: comma  
Header: NO_HEADER  
Numeric parse: PASS for 12/12  
NaN count: 0  
Inf count: 0  
Parse error count: 0

Observed layout: each sampled CSV is a single non-empty comma-separated numeric row containing 10,000,000 values. Column semantics remain `COLUMN_SEMANTICS_UNKNOWN`.

## 6. RF Numeric Structure

| File | Values | Min | Max | Mean | Std |
|---|---:|---:|---:|---:|---:|
| 00000L_21.csv | 10,000,000 | -110 | 114 | -0.0062254 | 3.80346246 |
| 00000H_21.csv | 10,000,000 | -180 | 160 | -0.0075958 | 2.84835544 |
| 00000L_30.csv | 10,000,000 | -114 | 124 | -0.0079303 | 3.63699320 |
| 00000H_30.csv | 10,000,000 | -221 | 224 | -0.0076009 | 5.25658784 |
| 00000L_40.csv | 10,000,000 | -100 | 104 | -0.0088865 | 3.49638147 |
| 00000H_40.csv | 10,000,000 | -24 | 24 | -0.0055144 | 2.74049246 |
| 10000L_0.csv | 10,000,000 | -9243 | 9336 | -0.0073772 | 627.38691495 |
| 10000H_0.csv | 10,000,000 | -164 | 176 | -0.0085365 | 4.01994590 |
| 10000L_10.csv | 10,000,000 | -9669 | 9691 | -0.0055290 | 612.13238919 |
| 10000H_10.csv | 10,000,000 | -187 | 209 | -0.0058960 | 5.68497547 |
| 10000L_20.csv | 10,000,000 | -11753 | 11092 | 0.0587460 | 1206.64706555 |
| 10000H_20.csv | 10,000,000 | -66 | 63 | -0.0067971 | 2.86780144 |

RF_NUMERIC_DATA: PASS

Basis: sampled CSVs are numeric, non-empty, finite, and non-constant. No sampled file showed large unparseable text, all-zero content, NaN, or Inf.

## 7. Filename Parsing

Pattern validated: `<BUI><L_or_H>_<segment_id>.csv`

TOTAL_CSV: 82  
VALID_FILENAMES: 82  
INVALID_FILENAMES: 0  
ZERO_BYTE_FILES: 0  
OPEN_FAILURES: 0  
BACKGROUND_SEGMENTS: 21-40  
DRONE_SEGMENTS: 0-20

FILENAME_PARSE_STATUS: PASS

## 8. Background Label Validation

BACKGROUND_LABEL_VALIDATION: PASS

Evidence:

- Official MATLAB aggregation code groups BUI `00000` as RF background activities.
- The extracted background files use BUI `00000` consistently.
- The local source audit records the official source-level mapping to No Drone / Background.

## 9. Drone Model Validation

DRONE_MODEL_LABEL_VALIDATION: PASS

Evidence:

- Official MATLAB aggregation and labeling code group `10000`, `10001`, `10010`, and `10011` as Bebop drone RF activities.
- The extracted drone validation files use BUI `10000` consistently.

## 10. Operating Mode Validation

OPERATING_MODE_LABEL_VALIDATION: PASS

Evidence:

- The source audit records the official BUI/mode mapping of `10000` to Parrot Bebop, ON / Connected.
- The current files use `10000L_<segment_id>.csv` and `10000H_<segment_id>.csv` consistently.

## 11. Segment Validation

SEGMENT_ID_VALIDATION: PASS

Evidence:

- Official aggregation code loads raw CSV files using BUI + L/H + `_` + segment number + `.csv`.
- Actual extracted filenames parse cleanly into BUI, L/H, and segment ID.
- L/H segment IDs match within background and drone groups.

Segment ID is treated as a segment or recording index, not as a timestamp.

## 12. Sample Rate Status

SAMPLE_RATE: UNKNOWN

No stored-file sample rate was inferred from row count or file size. Hardware capability values remain separate from stored dataset validation.

## 13. L/H Semantics

L_H_PHYSICAL_SEMANTICS: TWO_PART_SEGMENT_PAIR_CONFIRMED; EXACT_PHYSICAL_SEMANTICS_UNKNOWN

The current validation confirms that L and H form paired files for a shared BUI and segment ID. It does not assign a definitive physical meaning or per-file frequency range to L/H.

## 14. Anomalies

No blocking data corruption was found.

Informational note: the CSV files are single very long comma-separated numeric rows. Line-oriented preview commands can emit a full 90MB-plus row, so future readers should use streaming parsers.

## 15. Knowledge Index Feasibility

RF_KNOWLEDGE_INDEX_FEASIBLE: YES

A unified record can be generated from the observed structure:

```json
{
  "dataset": "DroneRF",
  "segment_id": 0,
  "drone_model": "Parrot Bebop",
  "operating_mode": "ON/Connected",
  "rf": {
    "L_file": "10000L_0.csv",
    "H_file": "10000H_0.csv"
  }
}
```

RF_MODEL_ASSOCIATION: STRONG  
RF_MODE_ASSOCIATION: STRONG

The association is supported by actual filenames plus official BUI/model/mode mapping.

## 16. Technical Result

TECHNICAL_VALIDATION: PASS

Reason:

- CSV extraction count matches archive inspection.
- All 82 CSV filenames parse successfully.
- All 82 CSV files are non-empty and file-stream readable.
- 12 sampled CSVs parse as numeric RF values without NaN, Inf, or parse errors.
- Background and drone L/H pair structures are consistent.
- Filename/BUI labels have official source-level evidence.

READY_FOR_FINAL_DATASET_EVALUATION: YES

Strictly not performed: FFT, STFT, spectrogram generation, filtering, downsampling, model training, classification accuracy testing, embedding, vector database generation, sample-rate inference, L/H physical-meaning inference, additional DroneRF downloads, or final dataset evaluation.
