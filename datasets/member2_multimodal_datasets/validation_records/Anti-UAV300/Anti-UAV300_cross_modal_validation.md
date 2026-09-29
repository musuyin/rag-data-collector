# Anti-UAV300 RGB-IR Cross-Modal Validation

## 1. Validated Sequences

- test/20190925_111757_1_1
- test/20190926_111509_1_7
- train/20190925_205804_1_7
- train/20190926_193515_1_6
- val/20190926_200510_1_8

## 2. Sequence-Level Pairing

| sequence | RGB video | IR video | visible annotation | infrared annotation |
|---|---:|---:|---:|---:|
| test/20190925_111757_1_1 | True | True | True | True |
| test/20190926_111509_1_7 | True | True | True | True |
| train/20190925_205804_1_7 | True | True | True | True |
| train/20190926_193515_1_6 | True | True | True | True |
| val/20190926_200510_1_8 | True | True | True | True |

SEQUENCE_LEVEL_PAIRING: PASS

## 3. Video Metadata

| sequence | RGB frames | IR frames | RGB fps | IR fps | RGB duration | IR duration | RGB resolution | IR resolution | codec |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| test/20190925_111757_1_1 | 1000 | 1000 | 20.0 | 20.0 | 50.0 | 50.0 | 1920x1080 | 640x512 | RGB=mpeg4; IR=mpeg4 |
| test/20190926_111509_1_7 | 1000 | 1000 | 20.0 | 20.0 | 50.0 | 50.0 | 1920x1080 | 640x512 | RGB=mpeg4; IR=mpeg4 |
| train/20190925_205804_1_7 | 950 | 950 | 20.0 | 20.0 | 47.5 | 47.5 | 1920x1080 | 640x512 | RGB=mpeg4; IR=mpeg4 |
| train/20190926_193515_1_6 | 1000 | 1000 | 20.0 | 20.0 | 50.0 | 50.0 | 1920x1080 | 640x512 | RGB=mpeg4; IR=mpeg4 |
| val/20190926_200510_1_8 | 493 | 493 | 20.0 | 20.0 | 24.65 | 24.65 | 1920x1080 | 640x512 | RGB=mpeg4; IR=mpeg4 |

## 4. Frame Count Comparison

| sequence | difference | absolute_difference | ratio RGB/IR | same frame count |
|---|---:|---:|---:|---:|
| test/20190925_111757_1_1 | 0 | 0 | 1.0 | True |
| test/20190926_111509_1_7 | 0 | 0 | 1.0 | True |
| train/20190925_205804_1_7 | 0 | 0 | 1.0 | True |
| train/20190926_193515_1_6 | 0 | 0 | 1.0 | True |
| val/20190926_200510_1_8 | 0 | 0 | 1.0 | True |

## 5. FPS Comparison

| sequence | RGB fps | IR fps | fps_difference | same fps |
|---|---:|---:|---:|---:|
| test/20190925_111757_1_1 | 20.0 | 20.0 | 0.0 | True |
| test/20190926_111509_1_7 | 20.0 | 20.0 | 0.0 | True |
| train/20190925_205804_1_7 | 20.0 | 20.0 | 0.0 | True |
| train/20190926_193515_1_6 | 20.0 | 20.0 | 0.0 | True |
| val/20190926_200510_1_8 | 20.0 | 20.0 | 0.0 | True |

## 6. Frame Index Pairing

Frame checks use frame 0, 25%, 50%, 75%, and last common frame. They verify index-level readability only.

| sequence | frame_index | RGB read | IR read | paired_read_status |
|---|---:|---:|---:|---|
| test/20190925_111757_1_1 | 0 | True | True | PASS |
| test/20190925_111757_1_1 | 249 | True | True | PASS |
| test/20190925_111757_1_1 | 499 | True | True | PASS |
| test/20190925_111757_1_1 | 749 | True | True | PASS |
| test/20190925_111757_1_1 | 999 | True | True | PASS |
| test/20190926_111509_1_7 | 0 | True | True | PASS |
| test/20190926_111509_1_7 | 249 | True | True | PASS |
| test/20190926_111509_1_7 | 499 | True | True | PASS |
| test/20190926_111509_1_7 | 749 | True | True | PASS |
| test/20190926_111509_1_7 | 999 | True | True | PASS |
| train/20190925_205804_1_7 | 0 | True | True | PASS |
| train/20190925_205804_1_7 | 237 | True | True | PASS |
| train/20190925_205804_1_7 | 474 | True | True | PASS |
| train/20190925_205804_1_7 | 711 | True | True | PASS |
| train/20190925_205804_1_7 | 949 | True | True | PASS |
| train/20190926_193515_1_6 | 0 | True | True | PASS |
| train/20190926_193515_1_6 | 249 | True | True | PASS |
| train/20190926_193515_1_6 | 499 | True | True | PASS |
| train/20190926_193515_1_6 | 749 | True | True | PASS |
| train/20190926_193515_1_6 | 999 | True | True | PASS |
| val/20190926_200510_1_8 | 0 | True | True | PASS |
| val/20190926_200510_1_8 | 123 | True | True | PASS |
| val/20190926_200510_1_8 | 246 | True | True | PASS |
| val/20190926_200510_1_8 | 369 | True | True | PASS |
| val/20190926_200510_1_8 | 492 | True | True | PASS |

## 7. Annotation Pairing

Annotation pairing rule: `visible.json[index]` maps to `visible.mp4` frame `index`; `infrared.json[index]` maps to `infrared.mp4` frame `index`; the same index links RGB and IR at frame-pair level.

| sequence | frame_index | visible annotation | infrared annotation | RGB index to IR index |
|---|---:|---|---|---|
| test/20190925_111757_1_1 | 0 | PASS | PASS | PASS |
| test/20190925_111757_1_1 | 249 | PASS | PASS | PASS |
| test/20190925_111757_1_1 | 499 | PASS | PASS | PASS |
| test/20190925_111757_1_1 | 749 | PASS | PASS | PASS |
| test/20190925_111757_1_1 | 999 | PASS | PASS | PASS |
| test/20190926_111509_1_7 | 0 | PASS | PASS | PASS |
| test/20190926_111509_1_7 | 249 | PASS | PASS | PASS |
| test/20190926_111509_1_7 | 499 | PASS | PASS | PASS |
| test/20190926_111509_1_7 | 749 | PASS | PASS | PASS |
| test/20190926_111509_1_7 | 999 | PASS | PASS | PASS |
| train/20190925_205804_1_7 | 0 | PASS | PASS | PASS |
| train/20190925_205804_1_7 | 237 | PASS | PASS | PASS |
| train/20190925_205804_1_7 | 474 | PASS | PASS | PASS |
| train/20190925_205804_1_7 | 711 | PASS | PASS | PASS |
| train/20190925_205804_1_7 | 949 | PASS | PASS | PASS |
| train/20190926_193515_1_6 | 0 | PASS | PASS | PASS |
| train/20190926_193515_1_6 | 249 | PASS | PASS | PASS |
| train/20190926_193515_1_6 | 499 | PASS | PASS | PASS |
| train/20190926_193515_1_6 | 749 | PASS | PASS | PASS |
| train/20190926_193515_1_6 | 999 | PASS | PASS | PASS |
| val/20190926_200510_1_8 | 0 | PASS | PASS | PASS |
| val/20190926_200510_1_8 | 123 | PASS | PASS | PASS |
| val/20190926_200510_1_8 | 246 | PASS | PASS | PASS |
| val/20190926_200510_1_8 | 369 | PASS | PASS | PASS |
| val/20190926_200510_1_8 | 492 | PASS | PASS | PASS |

## 8. Target Presence Agreement

Target presence agreement is recorded, not forced to be 100%. Differences can arise from modality-specific visibility, thermal response, occlusion, and annotation policy.

| sequence | total | both_present | both_absent | visible_only | infrared_only | agreement_rate |
|---|---:|---:|---:|---:|---:|---:|
| test/20190925_111757_1_1 | 1000 | 1000 | 0 | 0 | 0 | 1.0 |
| test/20190926_111509_1_7 | 1000 | 1000 | 0 | 0 | 0 | 1.0 |
| train/20190925_205804_1_7 | 950 | 950 | 0 | 0 | 0 | 1.0 |
| train/20190926_193515_1_6 | 1000 | 944 | 0 | 0 | 56 | 0.944 |
| val/20190926_200510_1_8 | 493 | 474 | 14 | 0 | 5 | 0.9898580121703854 |

Aggregate agreement rate: 0.9862705379248256

## 9. Timestamp Evidence

- TIMESTAMP_AVAILABLE: CONTAINER_TIMESTAMP_ONLY
- Container PTS is available in inspected MP4 streams.
- SENSOR_TIMESTAMP_AVAILABLE: NO
- MP4/container PTS is not treated as sensor hardware timestamp.

## 10. Synchronization Evidence

- SOURCE_SYNC_EVIDENCE: NOT_FOUND_FOR_HARD_SYNC
- SOURCE_NON_ALIGNMENT_EVIDENCE: PRESENT
- SYNCHRONIZATION_STATUS: FRAME_PAIRED_ONLY
- Real files support stable sequence/frame-index pairing, but this does not prove hardware-level synchronization.

## 11. Full Dataset Lightweight Pairing Scan

- total_sequences: 318
- both_modalities_present: 318
- same_frame_count_sequences: 318
- different_frame_count_sequences: 0
- same_fps_sequences: 318
- different_fps_sequences: 0
- same_annotation_count_sequences: 318
- different_annotation_count_sequences: 0
- annotation_matches_video_sequences: 318
- frame_pairing_candidate_sequences: 318
- FRAME_PAIRING_COVERAGE: 318 / 318
- Non-candidate sequences: none

## 12. RGB-IR Index Feasibility

A knowledge-management index can be built using dataset, sequence_id, frame_index, RGB video path, visible annotation, IR video path, and infrared annotation. This report does not bulk-generate the index.

RGB_IR_INDEX_FEASIBLE: YES

## 13. Limitations

- This step validates sequence/frame-index pairing, not hardware-level synchronization.
- MP4 container PTS is not treated as sensor timestamp.
- RGB and IR bounding boxes are not numerically compared because sensor resolution/FOV/position can differ.
- No image registration, feature matching, embeddings, or model training were performed.

## 14. Final Cross-Modal Result

- SEQUENCE_LEVEL_PAIRING: PASS
- FRAME_INDEX_PAIRING: PASS
- RGB_IR_FRAME_COUNT_MATCH: PASS
- RGB_IR_FPS_MATCH: PASS
- ANNOTATION_FRAME_PAIRING: PASS
- TIMESTAMP_AVAILABLE: CONTAINER_TIMESTAMP_ONLY
- SOURCE_SYNC_EVIDENCE: NOT_FOUND_FOR_HARD_SYNC
- SYNCHRONIZATION_STATUS: FRAME_PAIRED_ONLY
- RGB_IR_ASSOCIATION_STRENGTH: STRONG
- FRAME_PAIRING_COVERAGE: 318 / 318
- RGB_IR_INDEX_FEASIBLE: YES
- CROSS_MODAL_VALIDATION: PASS
- READY_FOR_FINAL_DATASET_EVALUATION: YES
- TARGET_PRESENCE_AGREEMENT: RECORDED; agreement_rate=0.9862705379248256; both_present=4368; both_absent=14; visible_only=0; infrared_only=61
