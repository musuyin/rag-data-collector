# MMAUD Cross-Modal Validation

Dataset: MMAUD

Subset: UG2+ val

Original or Derived: DERIVED_SUBSET

Scope: path, directory, filename timestamp, and local documentation/reference checks only. No PNG or NPY payload content was read.

## SEQUENCE ASSOCIATION

| Field | Value |
|---|---|
| Total Sequences | 16 |
| Fully Multimodal Sequences | 16 |
| Coverage | 16 / 16 |
| Result | PASS |

| sequence_id | camera | lidar360 | livox | radar | camera_count | lidar360_count | livox_count | radar_count |
|---|---|---|---|---|---|---|---|---|
| seq0001 | True | True | True | True | 147 | 50 | 50 | 74 |
| seq0002 | True | True | True | True | 151 | 51 | 51 | 76 |
| seq0003 | True | True | True | True | 153 | 51 | 51 | 76 |
| seq0004 | True | True | True | True | 157 | 52 | 52 | 78 |
| seq0005 | True | True | True | True | 150 | 51 | 50 | 76 |
| seq0006 | True | True | True | True | 150 | 50 | 50 | 75 |
| seq0007 | True | True | True | True | 150 | 50 | 50 | 75 |
| seq0008 | True | True | True | True | 148 | 50 | 50 | 75 |
| seq0009 | True | True | True | True | 151 | 49 | 50 | 75 |
| seq0010 | True | True | True | True | 149 | 50 | 50 | 74 |
| seq0011 | True | True | True | True | 152 | 51 | 51 | 75 |
| seq0012 | True | True | True | True | 153 | 51 | 51 | 77 |
| seq0013 | True | True | True | True | 150 | 50 | 50 | 75 |
| seq0014 | True | True | True | True | 153 | 51 | 51 | 77 |
| seq0015 | True | True | True | True | 157 | 52 | 52 | 79 |
| seq0016 | True | True | True | True | 155 | 35 | 51 | 77 |

## TIMESTAMP QUALITY

| Field | Value |
|---|---|
| Timestamp Unit | seconds |
| Rationale | Filename timestamps are epoch-like numeric values around 1.706e9, and adjacent differences imply about 30 Hz camera, 10 Hz LiDAR/Livox, and 15 Hz radar. |

| Modality | Parsed | Parse Failures | Duplicates | Min Timestamp | Max Timestamp | Median Interval ms | Estimated Hz | Gaps |
|---|---|---|---|---|---|---|---|---|
| Camera | 2426 | 0 | 0 | 1706255054.409385 | 1706258752.912320 | 32.147 | 31.107 | 0 |
| LiDAR360 | 794 | 0 | 0 | 1706255054.400078 | 1706258752.900885 | 99.967 | 10.003 | 0 |
| Livox Avia | 810 | 0 | 0 | 1706255054.417480 | 1706258752.894309 | 99.966 | 10.003 | 0 |
| Radar | 1214 | 0 | 0 | 1706255054.405226 | 1706258752.911294 | 66.909 | 14.946 | 0 |

## CAMERA TO LIDAR360

| Metric | Value |
|---|---|
| Matched Frames | 2426 |
| Mean Delta | 27.162 ms |
| Median Delta | 20.182 ms |
| P95 Delta | 47.997 ms |
| Max Delta | 151.030 ms |
| Within 10ms | 6.68% |
| Within 20ms | 49.71% |
| Within 50ms | 97.44% |
| Within 100ms | 99.71% |

## CAMERA TO LIVOX

| Metric | Value |
|---|---|
| Matched Frames | 2426 |
| Mean Delta | 26.603 ms |
| Median Delta | 18.995 ms |
| P95 Delta | 49.834 ms |
| Max Delta | 90.890 ms |
| Within 10ms | 6.35% |
| Within 20ms | 53.30% |
| Within 50ms | 98.85% |
| Within 100ms | 100.00% |

## CAMERA TO RADAR

| Metric | Value |
|---|---|
| Matched Frames | 2426 |
| Mean Delta | 16.764 ms |
| Median Delta | 17.367 ms |
| P95 Delta | 32.431 ms |
| Max Delta | 55.948 ms |
| Within 10ms | 31.62% |
| Within 20ms | 53.09% |
| Within 50ms | 99.88% |
| Within 100ms | 100.00% |
| Unique Radar Matches | 1213 |
| Camera Frames Per Radar Sample | {"mean": 2.0, "median": 2.0, "max": 3} |

## OTHER ASSOCIATIONS

| Association | Matched Frames | Median Delta ms | P95 Delta ms | Max Delta ms |
|---|---|---|---|---|
| lidar360_to_radar | 794 | 18.617 | 31.914 | 55.318 |
| livox_to_radar | 810 | 16.729 | 31.647 | 61.280 |

## CALIBRATION

| Field | Value |
|---|---|
| Status | PARTIAL |
| Evidence | No calibration file was found inside current val.zip extraction or local samples; source audit documents official calibration/reference resources.<br>| MMAUD official page | Level 1 official dataset page | https://ntu-aris.github.io/MMAUD/ | overview, sensor summary, V1/V2/V3 downloads, V1 sizes/durations, V2/V3 unknown sizes, calibration link, 2D baseline link, citation, licence | 2026-09-20 |<br>| calibration assets | fisheye calibration Google Drive link; CAD/calibration references | official page |<br>| cross-modal synchronization | PARTIAL | timestamps and calibration exist, but the paper explicitly reports synchronization challenges. |<br>- complete transform/coordinate metadata files before sample inspection<br>- calibration/fisheye calibration resources are linked.<br>- the paper describes camera-to-LiDAR calibration and CAD-based references for audio/radar alignment.<br>| modalities | fisheye camera images, mmWave radar, LiDAR, Leica ground truth | |

## REFERENCE / GROUND TRUTH

| Field | Value |
|---|---|
| Status | NOT_FOUND |
| REFERENCE_MATCH_STATUS | NOT_TESTED |
| Evidence | No local UG2+ reference/pose/ground-truth CSV was found for this extracted val subset.<br>| MMAUD arXiv paper | Level 2 original paper | https://arxiv.org/abs/2402.03706 | paper title, authors, ICRA 2024 status, DOI, abstract, dataset purpose | 2026-09-20 |<br>| MMAUD paper HTML | Level 2 original paper text | https://arxiv.org/html/2402.03706 | sensor setup, dataset format, ROS topics, timestamps, sequence count, split, ground truth rate, synchronization limitations | 2026-09-20 |<br>| tasks | detection; classification; tracking; trajectory/3D position estimation | official heading and paper |<br>| confirmed modalities | RGB image/image stream, audio, radar, LiDAR, trajectory/ground truth, text metadata | official page and paper |<br>| calibration assets | fisheye calibration Google Drive link; CAD/calibration references | official page |<br>| Leica ground truth rate | 5 Hz | paper | |

## SYNCHRONIZATION

| Field | Value |
|---|---|
| Status | LIKELY_SYNCHRONIZED |
| Explanation | All modalities share sequence IDs and parsable filename timestamps; nearest-match medians are within one expected camera/radar/LiDAR frame interval. The source audit still notes sensor synchronization limitations, so strict synchronization is not confirmed. |

## CROSS-MODAL ASSOCIATION

| Field | Value |
|---|---|
| Association Strength | MEDIUM |
| Sequence Level Association | PASS |
| Timestamp Association | PASS |

## KNOWLEDGE SYSTEM READINESS

| Field | Value |
|---|---|
| CROSS_MODAL_INDEX_FEASIBLE | YES |
| Explanation | A sequence_id + timestamp nearest-neighbor index is technically feasible from filenames. Local calibration/reference support is not complete, so geometric or pose-level assertions should wait. |

## PROBLEMS

- `missing_calibration`: No local calibration matrices/transforms were found in val.zip extraction or current samples.
- `missing_reference_csv`: No local UG2+ reference/pose/ground-truth CSV was available for matching.

## FINAL RESULT

| Field | Value |
|---|---|
| SEQUENCE_LEVEL_ASSOCIATION | PASS |
| TIMESTAMP_ASSOCIATION | PASS |
| CAMERA_LIDAR360_MEDIAN_DELTA_MS | 20.182 |
| CAMERA_LIVOX_MEDIAN_DELTA_MS | 18.995 |
| CAMERA_RADAR_MEDIAN_DELTA_MS | 17.367 |
| CALIBRATION_STATUS | PARTIAL |
| SYNCHRONIZATION_STATUS | LIKELY_SYNCHRONIZED |
| ASSOCIATION_STRENGTH | MEDIUM |
| CROSS_MODAL_INDEX_FEASIBLE | YES |
| CROSS_MODAL_VALIDATION | PARTIAL |
| READY_FOR_FINAL_DATASET_EVALUATION | YES |

