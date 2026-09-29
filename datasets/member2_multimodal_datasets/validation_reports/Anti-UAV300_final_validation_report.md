# Anti-UAV300 Final Validation Report

## 1. Dataset Overview

| Field | Value |
|---|---|
| Dataset | Anti-UAV300 |
| Dataset Family | Anti-UAV |
| Related Versions | Anti-UAV410; Anti-UAV600 |
| Dataset Type | PAIRED RGB-IR TRACKING DATASET |
| Not Claimed As | HARD-SYNCHRONIZED SENSOR DATASET |
| Primary Modalities | RGB / Visible; Thermal / Infrared |
| Final Dataset Status | PARTIALLY_VERIFIED |
| Project Readiness | CROSS_MODAL_READY |

Anti-UAV300 is now validated for real RGB file readability, real IR file readability, annotation parsing, annotation-to-frame matching, and RGB-IR frame pairing through `sequence_id + frame_index`. Hard hardware synchronization remains not confirmed.

## 2. Official Sources

Inputs reviewed for this final evaluation:

- `reports/Anti-UAV300_source_audit.md`
- `reports/Anti-UAV300_sample_candidates.md`
- `samples/Anti-UAV300/download_manifest.json`
- `validation/Anti-UAV300_download_validation.md`
- `validation/Anti-UAV300_download_validation.json`
- `validation/Anti-UAV300_file_inspection.md`
- `validation/Anti-UAV300_file_inspection.json`
- `validation/Anti-UAV300_cross_modal_validation.md`
- `validation/Anti-UAV300_cross_modal_validation.json`
- `datasets/cards/Anti-UAV300.md`
- `datasets/cards/Anti-UAV300.json`

Conflict notes retained:

- CONFLICT: earlier Dataset Card / Registry said full package download was deferred and technical validation was NOT_TESTED; later explicit approval downloaded Anti-UAV-RGBT.zip and completed PASS validation.
- CONFLICT: source-level paper evidence described 25 FPS, while actual validated archive videos report 20 FPS for RGB and IR in the inspected sample and full metadata scan.
- CONFLICT: source-level repository folder-tree evidence suggested JPG image-sequence layout, while the actual official archive contains MP4 videos plus JSON annotations.

## 3. Data Scale

| Field | Value |
|---|---|
| Official Package | Anti-UAV-RGBT.zip |
| Archive Size | 6,037,566,331 bytes |
| SHA256 | ed7d80bbd8ca8e01ea784c64eb0782eae8b3a1572177535c0fada9beb53fdca8 |
| Archive File Count | 1276 |
| Archive Directory Count | 322 |
| Estimated Extracted Size | 6,720,200,225 bytes |
| Sequence Count | 318 RGB-T video pairs |
| Split Count | train=160; val=67; test=91 |
| Metadata-Derived RGB Frames | 296,901 |
| Metadata-Derived IR Frames | 296,901 |

## 4. Validated Sample

| Field | Value |
|---|---|
| Deep Technical Validation | 5 selected sequences |
| Selected Sequences | test/20190925_111757_1_1; test/20190926_111509_1_7; train/20190925_205804_1_7; train/20190926_193515_1_6; val/20190926_200510_1_8 |
| Full Dataset Lightweight Pairing Scan | 318 / 318 |

Five sequences were deeply inspected with sampled frame decoding and JSON parsing. All 318 sequences were checked through lightweight metadata and structure validation. This is not a claim that every frame was decoded pixel-by-pixel.

## 5. RGB Data

| Field | Value |
|---|---|
| RGB_PRESENT | YES |
| RGB_READABILITY | PASS |
| RGB_ANNOTATION_MATCH | PASS |
| RGB_FRAME_STRUCTURE | PASS |
| Observed File | visible.mp4 |
| Codec | mpeg4 |
| Resolution | 1920x1080 in selected validated sample |
| FPS | 20.0 observed in actual archive metadata |

## 6. Infrared Data

| Field | Value |
|---|---|
| IR_PRESENT | YES |
| IR_READABILITY | PASS |
| IR_ANNOTATION_MATCH | PASS |
| IR_FRAME_STRUCTURE | PASS |
| Observed File | infrared.mp4 |
| Codec | mpeg4 |
| Resolution | 640x512 in selected validated sample |
| FPS | 20.0 observed in actual archive metadata |

## 7. Annotation

| Field | Value |
|---|---|
| ANNOTATION_PARSE | PASS |
| BBOX_FORMAT | [x, y, w, h] |
| TARGET_PRESENCE_FIELD | exist |
| RGB_ANNOTATION_MATCH | PASS |
| IR_ANNOTATION_MATCH | PASS |
| ANNOTATION_FRAME_PAIRING | PASS |
| ANNOTATION_VALIDATION | PASS |

## 8. Sequence-Level Pairing

| Field | Value |
|---|---|
| SEQUENCE_LEVEL_PAIRING | PASS |
| both_modalities_present | 318 |
| total_sequences | 318 |

## 9. Frame-Level Pairing

| Field | Value |
|---|---|
| FRAME_INDEX_PAIRING | PASS |
| RGB_IR_FRAME_COUNT_MATCH | PASS |
| RGB_IR_FPS_MATCH | PASS |
| same_frame_count_sequences | 318 |
| same_fps_sequences | 318 |
| same_annotation_count_sequences | 318 |
| frame_pairing_candidate_sequences | 318 |
| FRAME_PAIRING_COVERAGE | 318 / 318 |

`sequence_id + frame_index` is validated as a stable and reproducible cross-modal key. This means frame pairing is confirmed; it does not prove hardware-clock synchronization.

## 10. Target Presence Agreement

| Field | Value |
|---|---|
| agreement_rate | 0.9862705379248256 (~98.63%) |
| both_present | 4368 |
| both_absent | 14 |
| visible_only | 0 |
| infrared_only | 61 |
| total_compared | 4443 |

RGB / IR target-presence annotations are highly consistent but not identical. `infrared_only=61` is retained as a real observed difference.

## 11. Synchronization Status

| Field | Value |
|---|---|
| Frame Pairing | CONFIRMED |
| Hard Synchronization | NOT CONFIRMED |
| TIMESTAMP_AVAILABLE | CONTAINER_TIMESTAMP_ONLY |
| SOURCE_SYNC_EVIDENCE | NOT_FOUND_FOR_HARD_SYNC |
| SYNCHRONIZATION_STATUS | FRAME_PAIRED_ONLY |

Container PTS exists in the inspected MP4 streams, but no sensor hardware timestamp was found. Anti-UAV300 should therefore be described as `FRAME_PAIRED_ONLY`, not `HARD_SYNCHRONIZED_CONFIRMED`.

## 12. Cross-Modal Index Feasibility

`RGB_IR_INDEX_FEASIBLE: YES`

Feasible index shape:

```json
{
  "dataset": "Anti-UAV300",
  "sequence_id": "...",
  "frame_index": 123,
  "visible": {
    "video": ".../visible.mp4",
    "frame_index": 123,
    "annotation": {"exist": 1, "bbox": [0, 0, 0, 0]}
  },
  "infrared": {
    "video": ".../infrared.mp4",
    "frame_index": 123,
    "annotation": {"exist": 1, "bbox": [0, 0, 0, 0]}
  }
}
```

This report confirms feasibility; it does not bulk-generate the full index.

## 13. Collection Environment

`COLLECTION_ENVIRONMENT_VALIDATION: PARTIAL`

Source-level environment evidence remains useful: outdoor scenes, day/night coverage, sky/building/cloud backgrounds, occlusion, fast motion, scale variation, background clutter, low illumination, and thermal crossover are documented. These are not all re-measured from every local sample.

## 14. Sensor Parameters

`SENSOR_PARAMETER_VALIDATION: PARTIAL`

Validated local media metadata confirms RGB 1920x1080 at 20 FPS and IR 640x512 at 20 FPS in the selected sample, with all 318 sequences matching frame count/FPS pairing conditions. Camera model, FOV, calibration, spectral band, and hardware synchronization metadata remain UNKNOWN.

## 15. License

`LICENSE_VALIDATION: RISK`

The repository MIT license is not treated as Anti-UAV300 dataset license permission. Dataset-level terms for commercial use, redistribution, and modification remain unconfirmed. Raw data should not be copied into public delivery artifacts.

## 16. Limitations

- No hard synchronization evidence: sensor-level trigger or unified hardware timestamp was not confirmed.
- Only MP4/container timestamps are available; they are not treated as sensor timestamps.
- Frame pairing is confirmed, but sensor-level synchronization is not.
- RGB / IR target presence agreement is high but not perfect: infrared_only=61 was observed in the selected validation sample.
- Dataset license remains RISK because explicit dataset-level license terms were not confirmed.
- Five sequences were deeply inspected; all 318 sequences were checked through lightweight metadata and structural pairing validation.
- Raw Anti-UAV300 data should not be redistributed in public delivery artifacts unless rights are explicitly confirmed.

## 17. Recommended Uses

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

## 18. Final Status

| Field | Value |
|---|---|
| SOURCE_VALIDATION | PASS |
| TECHNICAL_VALIDATION | PASS |
| ANNOTATION_VALIDATION | PASS |
| CROSS_MODAL_VALIDATION | PASS |
| LICENSE_VALIDATION | RISK |
| COLLECTION_ENVIRONMENT_VALIDATION | PARTIAL |
| SENSOR_PARAMETER_VALIDATION | PARTIAL |
| RGB_IR_ASSOCIATION_STRENGTH | STRONG |
| FRAME_PAIRING_COVERAGE | 318 / 318 |
| SYNCHRONIZATION_STATUS | FRAME_PAIRED_ONLY |
| RGB_IR_INDEX_FEASIBLE | YES |
| FINAL_DATASET_STATUS | PARTIALLY_VERIFIED |
| PROJECT_READINESS | CROSS_MODAL_READY |
| READY_FOR_PROJECT_DATASET_DELIVERY | YES |

Final interpretation: Anti-UAV300 is ready for this project's RGB-IR cross-modal knowledge-management delivery as a frame-paired dataset. It is not marked fully `VERIFIED` because hard synchronization is not confirmed, explicit dataset-level license terms remain unresolved, and several sensor/environment parameters remain partial or unknown.
