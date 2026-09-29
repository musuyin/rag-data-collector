# DroneRF Final Validation Report

Final evaluation date: 2026-09-29  
Dataset: DroneRF  
Official version: Mendeley Data v1  
Final dataset status: VERIFIED  
Project readiness: BASIC_USABLE

## 1. Dataset Overview

DroneRF is an RF signal dataset for drone detection, identification, and operating-mode classification.

| Field | Value |
|---|---|
| Dataset | DroneRF |
| Official Version | Mendeley Data v1 |
| Primary Modality | RF |
| Secondary Modality | Text Metadata / Labels |
| Dataset Type | RF SIGNAL DATASET |
| Official URL | https://data.mendeley.com/datasets/f4c2b4n755/1 |
| DOI | 10.17632/f4c2b4n755.1 |

DroneRF should not be described as a synchronized multi-sensor multimodal dataset. Its current project value is RF signal data plus drone model and operating-mode metadata.

## 2. Official Sources

| Source | Role |
|---|---|
| Mendeley Data v1 | Official dataset repository |
| Data in Brief article | Dataset scale, RF CSV structure, acquisition setup, labels |
| Official GitHub repository | MATLAB/Python/LabVIEW processing and labeling code |
| MATLAB aggregation script | Confirms paired L/H raw CSV loading and BUI groups |
| MATLAB labeling script | Confirms drone/no-drone, drone model, and BUI/mode label construction |

No blocking conflict was found across the final-stage inputs. Earlier `SOURCE_AUDIT_ONLY` and `NOT_DOWNLOADED` fields are superseded by the later approved download and file-inspection reports.

## 3. Data Scale

Official full dataset:

| Field | Value |
|---|---|
| Size | >40GB |
| Segments | 227 |
| CSV record files | 454 |
| Drone models | Parrot Bebop; Parrot AR Drone; DJI Phantom |
| Background | No Drone / RF background |

This final evaluation does not claim the full >40GB DroneRF dataset was exhaustively inspected.

## 4. Validated Sample

Validation was performed on a selected official raw RF subset.

| Field | Value |
|---|---|
| Source | Official Mendeley Data v1 RAR file objects |
| Compressed files | 4 RAR archives |
| Compressed size | 714,741,588 bytes |
| Extracted CSV count | 82 |
| Extracted size | 7,816,289,911 bytes |
| Background subset | 20 L + 20 H CSV, BUI `00000`, segments 21-40 |
| Drone subset | 21 L + 21 H CSV, BUI `10000`, Parrot Bebop ON / Connected, segments 0-20 |

Validated archives:

| Role | Archive | CSV Count | Segment IDs |
|---|---|---:|---|
| BACKGROUND_L | RF Data_00000_L2.rar | 20 | 21-40 |
| BACKGROUND_H | FR Data_00000_H2.rar | 20 | 21-40 |
| DRONE_L | RF Data_10000_L.rar | 21 | 0-20 |
| DRONE_H | RF Data_10000_H.rar | 21 | 0-20 |

## 5. RF Data Representation

| Field | Status |
|---|---|
| RAW_RF | PASS |
| CSV_READABILITY | PASS |
| NUMERIC_PARSE | PASS |
| IQ | NO_CONFIRMED |
| stored frequency spectrum | NO_PRECOMPUTED |
| stored spectrogram | NO |

The validated CSV files contain numeric time-domain RF values. No FFT, STFT, spectrogram generation, embedding, or model training was performed.

## 6. File Structure

Extraction produced exactly 82 CSV files, matching archive inspection.

| Check | Result |
|---|---|
| EXTRACTION_STATUS | PASS |
| EXTRACTED_CSV_COUNT | 82 |
| empty files | 0 |
| unreadable file streams | 0 |
| unexpected extensions | 0 |
| filename parse success | 82 / 82 |

Filename pattern:

```text
<BUI><L_or_H>_<segment_id>.csv
```

## 7. L/H Pair Structure

| Pair | Result |
|---|---|
| Background L/H segment match | PASS, segment IDs 21-40 |
| Drone L/H segment match | PASS, segment IDs 0-20 |
| Pair structure compatibility | YES for sampled pairs |

L/H is validated as a two-part segment pair. Exact physical semantics remain unknown.

## 8. Label System

Label source:

```text
Filename / BUI + official mapping / labeling scripts
```

| Label Check | Result |
|---|---|
| Background Label | PASS |
| Drone Model Label | PASS |
| Operating Mode Label | PASS |
| Segment ID | PASS |

The validation confirms stable associations:

```text
RF File -> Filename / BUI -> Drone Model
RF File -> Filename / BUI -> Operating Mode
```

## 9. Drone Model Association

RF_MODEL_ASSOCIATION: STRONG

Reason: actual filenames in the validated subset parse to BUI values, and official mapping / labeling scripts associate those BUI values with drone model classes. In this subset, `10000` maps to Parrot Bebop.

`STRONG` here refers to label-system association, not cross-sensor synchronization.

## 10. Operating Mode Association

RF_MODE_ASSOCIATION: STRONG

Reason: actual filenames in the validated subset use BUI `10000`, and the official mapping used by the project associates `10000` with Parrot Bebop ON / Connected.

`STRONG` here means a single RF file or segment can be linked to an operating-mode label through the official filename/BUI system.

## 11. Collection Environment

COLLECTION_ENVIRONMENT_VALIDATION: PARTIAL

The source audit confirms a laboratory setting at Qatar University and drone-controller RF collection context. Per-file distance, line-of-sight, interference, and session-level environment metadata remain unknown.

## 12. RF Acquisition Parameters

SENSOR_PARAMETER_VALIDATION: PARTIAL

| Parameter | Status |
|---|---|
| receiver model | source-confirmed |
| RF hardware range | source-confirmed |
| bandwidth setup | source-confirmed at source level |
| stored sample rate | UNKNOWN |
| exact L/H physical semantics | UNKNOWN |

The 200 MS/s value is a hardware maximum I/Q sample-rate parameter and must not be treated as the stored DroneRF CSV sample rate.

## 13. Technical Validation

TECHNICAL_VALIDATION: PASS

| Check | Result |
|---|---|
| Download integrity | PASS |
| SHA-256 | PASS for 4/4 archives |
| RAR integrity | PASS |
| Extraction | PASS |
| CSV readability | PASS |
| Numeric parse | PASS |
| NaN / Inf in sampled CSVs | none detected |
| Parse errors in sampled CSVs | 0 |
| L/H pair structure | PASS |
| Filename parsing | PASS |

Twelve sampled CSV files were stream-parsed, covering Background segments 21, 30, 40 and Drone segments 0, 10, 20 with both L and H files. Each sampled CSV contained 10,000,000 numeric values.

## 14. Knowledge Index Feasibility

RF_KNOWLEDGE_INDEX_FEASIBLE: YES

The validated structure supports a unified knowledge record:

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

For the broader UAV Multimodal Knowledge System, DroneRF is useful for:

```text
Drone Entity -> RF Representation
Drone Entity -> Operating Mode -> RF Samples
```

This is KNOWLEDGE-LEVEL CROSS-MODAL ASSOCIATION, not SENSOR-LEVEL SYNCHRONIZATION.

## 15. License

LICENSE_VALIDATION: PASS

| Field | Value |
|---|---|
| license_name | CC BY 4.0 |
| research_use | YES |
| commercial_use | YES under CC BY 4.0 terms unless additional platform terms apply |
| redistribution | YES with attribution |
| citation_required | YES |

The official code repository uses Apache-2.0; that is separate from the dataset license.

## 16. Limitations

| Limitation | Status |
|---|---|
| Stored sample rate | UNKNOWN |
| Exact L/H physical semantics | UNKNOWN |
| Full >40GB dataset inspection | NOT_DONE |
| RGB / Audio / Radar / LiDAR synchronization | NOT_AVAILABLE |
| Sensor-level multimodal synchronization | NOT_APPLICABLE |
| FFT / STFT / spectrogram validation | NOT_DONE |
| Embedding / model training / classification validation | NOT_DONE |

These limitations are retained in the final status and should not be hidden by the `VERIFIED` label.

## 17. Recommended Uses

| Use | Status |
|---|---|
| RF data storage | VALIDATED_FUNCTION |
| RF metadata indexing | VALIDATED_FUNCTION |
| Drone model -> RF retrieval | VALIDATED_FUNCTION |
| Operating mode -> RF retrieval | VALIDATED_FUNCTION |
| RF knowledge graph | VALIDATED_FUNCTION |
| Multimodal knowledge system | VALIDATED_FUNCTION at knowledge layer |
| RF feature extraction experiments | FUTURE_USE |
| Spectrogram generation | FUTURE_USE |
| RF embedding experiments | FUTURE_USE |
| Classification experiments | FUTURE_USE |

## 18. Final Status

| Field | Value |
|---|---|
| SOURCE_VALIDATION | PASS |
| TECHNICAL_VALIDATION | PASS |
| LABEL_VALIDATION | PASS |
| RF_STRUCTURE_VALIDATION | PASS |
| LICENSE_VALIDATION | PASS |
| COLLECTION_ENVIRONMENT_VALIDATION | PARTIAL |
| SENSOR_PARAMETER_VALIDATION | PARTIAL |
| FINAL_DATASET_STATUS | VERIFIED |
| PROJECT_READINESS | BASIC_USABLE |

Final interpretation: DroneRF is verified for the project-relevant RF structure, label association, and file readability on an official selected raw RF subset. It is not a synchronized multimodal sensor dataset, and the full >40GB dataset has not been exhaustively inspected.
