# Anti-UAV300 Dataset Card

Last checked: 2026-09-29  
Status: PARTIALLY_VERIFIED  
Project readiness: CROSS_MODAL_READY  
Dataset type: PAIRED RGB-IR TRACKING DATASET

## Basic Information

| Field | Value |
|---|---|
| dataset_id | Anti-UAV300 |
| dataset_family | Anti-UAV |
| related_versions | Anti-UAV410; Anti-UAV600 |
| full_name | Anti-UAV: A Large Multi-Modal Benchmark for UAV Tracking |
| version | Anti-UAV300 |
| official_url | https://anti-uav.github.io/ |
| repository_url | https://github.com/ZhaoJ9014/Anti-UAV |
| paper_url | https://arxiv.org/abs/2101.08466 |
| download_url | https://drive.google.com/file/d/1NPYaop35ocVTYWHOYQQHn8YHsM9jmLGr/view |

Anti-UAV300 is treated as a paired RGB-IR tracking dataset. It is not treated as a hard-synchronized sensor dataset because no hardware trigger or sensor timestamp evidence was confirmed.

## Modalities

| Field | Value |
|---|---|
| RGB / visible video | YES |
| Thermal / infrared video | YES |
| Annotation | YES |
| Audio / RF / Radar / LiDAR | NO for Anti-UAV300 |

## Data Scale And Validation Scope

| Field | Value |
|---|---|
| Official package | Anti-UAV-RGBT.zip |
| Archive size | 6,037,566,331 bytes |
| SHA256 | ed7d80bbd8ca8e01ea784c64eb0782eae8b3a1572177535c0fada9beb53fdca8 |
| Sequence count | 318 RGB-T video pairs |
| Archive file count | 1276 |
| Validated deep sample | 5 selected sequences |
| Full dataset lightweight scan | 318 / 318 sequences |
| Metadata-derived RGB frames | 296,901 |
| Metadata-derived IR frames | 296,901 |

Deep technical validation decoded sampled frames and parsed annotations for five sequences. The 318-sequence scan validated metadata, structure, frame counts, FPS, annotation counts, and frame-pairing candidacy without decoding every frame.

## RGB Data

| Field | Value |
|---|---|
| RGB_PRESENT | YES |
| RGB_READABILITY | PASS |
| RGB_ANNOTATION_MATCH | PASS |
| RGB_FRAME_STRUCTURE | PASS |
| Observed file | visible.mp4 |
| Codec | mpeg4 |
| Selected-sample resolution | 1920x1080 |
| FPS | 20.0 |

## Infrared Data

| Field | Value |
|---|---|
| IR_PRESENT | YES |
| IR_READABILITY | PASS |
| IR_ANNOTATION_MATCH | PASS |
| IR_FRAME_STRUCTURE | PASS |
| Observed file | infrared.mp4 |
| Codec | mpeg4 |
| Selected-sample resolution | 640x512 |
| FPS | 20.0 |

## Annotation

| Field | Value |
|---|---|
| ANNOTATION_PARSE | PASS |
| BBOX_FORMAT | [x, y, w, h] |
| TARGET_PRESENCE_FIELD | exist |
| RGB_ANNOTATION_MATCH | PASS |
| IR_ANNOTATION_MATCH | PASS |
| ANNOTATION_FRAME_PAIRING | PASS |
| ANNOTATION_VALIDATION | PASS |

## RGB-IR Pairing

| Field | Value |
|---|---|
| SEQUENCE_LEVEL_PAIRING | PASS |
| FRAME_INDEX_PAIRING | PASS |
| RGB_IR_FRAME_COUNT_MATCH | PASS |
| RGB_IR_FPS_MATCH | PASS |
| FRAME_PAIRING_COVERAGE | 318 / 318 |
| RGB_IR_ASSOCIATION_STRENGTH | STRONG |
| RGB_IR_INDEX_FEASIBLE | YES |

## Target Presence Agreement

| Field | Value |
|---|---|
| agreement_rate | 0.9862705379248256 (~98.63%) |
| both_present | 4368 |
| both_absent | 14 |
| visible_only | 0 |
| infrared_only | 61 |

The visible and infrared annotations are highly consistent for target presence, but not identical. This must not be described as perfect agreement or 100% synchronization.

## Synchronization Status

| Field | Value |
|---|---|
| Frame Pairing | CONFIRMED |
| Hard Synchronization | NOT CONFIRMED |
| TIMESTAMP_AVAILABLE | CONTAINER_TIMESTAMP_ONLY |
| SOURCE_SYNC_EVIDENCE | NOT_FOUND_FOR_HARD_SYNC |
| SYNCHRONIZATION_STATUS | FRAME_PAIRED_ONLY |

Anti-UAV300's project value here is frame-level cross-modal pairing, not hardware clock synchronization.

## License

| Field | Value |
|---|---|
| LICENSE_VALIDATION | RISK |
| license_name | UNKNOWN |
| commercial_use | UNKNOWN |
| redistribution | UNKNOWN |

The repository MIT license is treated as code licensing only. Dataset-level redistribution and commercial-use permissions remain unconfirmed, so raw data should not be included in public delivery artifacts.

## Validation Summary

| Field | Value |
|---|---|
| SOURCE_VALIDATION | PASS |
| TECHNICAL_VALIDATION | PASS |
| ANNOTATION_VALIDATION | PASS |
| CROSS_MODAL_VALIDATION | PASS |
| LICENSE_VALIDATION | RISK |
| COLLECTION_ENVIRONMENT_VALIDATION | PARTIAL |
| SENSOR_PARAMETER_VALIDATION | PARTIAL |
| FINAL_DATASET_STATUS | PARTIALLY_VERIFIED |
| PROJECT_READINESS | CROSS_MODAL_READY |

## Conflicts Resolved Or Retained

- CONFLICT: earlier Dataset Card / Registry said full package download was deferred and technical validation was NOT_TESTED; later explicit approval downloaded Anti-UAV-RGBT.zip and completed PASS validation.
- CONFLICT: source-level paper evidence described 25 FPS, while actual validated archive videos report 20 FPS for RGB and IR in the inspected sample and full metadata scan.
- CONFLICT: source-level repository folder-tree evidence suggested JPG image-sequence layout, while the actual official archive contains MP4 videos plus JSON annotations.

## Limitations

- No hard synchronization evidence: sensor-level trigger or unified hardware timestamp was not confirmed.
- Only MP4/container timestamps are available; they are not treated as sensor timestamps.
- Frame pairing is confirmed, but sensor-level synchronization is not.
- RGB / IR target presence agreement is high but not perfect: infrared_only=61 was observed in the selected validation sample.
- Dataset license remains RISK because explicit dataset-level license terms were not confirmed.
- Five sequences were deeply inspected; all 318 sequences were checked through lightweight metadata and structural pairing validation.
- Raw Anti-UAV300 data should not be redistributed in public delivery artifacts unless rights are explicitly confirmed.

## Recommended Uses

- RGB -> IR retrieval: VALIDATED_STRUCTURE
- IR -> RGB retrieval: VALIDATED_STRUCTURE
- RGB / IR tracking research: VALIDATED_DATA_ACCESS
- RGB-T multimodal storage: VALIDATED_STRUCTURE
- frame-level cross-modal indexing: VALIDATED_STRUCTURE
- visible -> infrared association: VALIDATED_STRUCTURE
- infrared -> visible association: VALIDATED_STRUCTURE
- multimodal knowledge base: VALIDATED_STRUCTURE
- later multimodal embedding experiments: FUTURE_USE
- model training: FUTURE_USE
- tracking accuracy evaluation: FUTURE_USE

