# Anti-UAV300 File Inspection Validation

## Scope

This report validates a small selected sample from the extracted Anti-UAV-RGBT package. It does not claim RGB/IR synchronization, model readiness, or redistribution permission.

## Summary

- EXTRACTION_STATUS: PASS
- VALIDATED_SEQUENCE_COUNT: 5
- RGB_READABILITY: PASS
- IR_READABILITY: PASS
- ANNOTATION_PARSE: PASS
- BBOX_FORMAT: [x, y, w, h]
- TARGET_PRESENCE_FIELD: exist
- RGB_ANNOTATION_MATCH: PASS
- IR_ANNOTATION_MATCH: PASS
- RGB_FRAME_COUNT_STATUS: CONSISTENT_WITH_VISIBLE_ANNOTATION
- IR_FRAME_COUNT_STATUS: CONSISTENT_WITH_INFRARED_ANNOTATION
- FRAME_FILENAME_CORRESPONDENCE: NOT_APPLICABLE_VIDEO_CONTAINER
- FRAME_INDEX_CORRESPONDENCE: YES
- FRAME_PAIRING_FEASIBLE: YES
- COMPLETE_SEQUENCE_COVERAGE: YES
- TECHNICAL_VALIDATION: PASS
- READY_FOR_RGB_IR_CROSS_MODAL_VALIDATION: YES

## Extraction

- Source archive: `samples\Anti-UAV300\raw\Anti-UAV-RGBT.zip`
- Extracted path: `samples\Anti-UAV300\extracted`
- Extracted file count: 1276
- Extracted size bytes: 6720200225

## Selected Sequences

| split | sequence_id | RGB | IR | annotation | RGB frames | IR frames | annotation records |
|---|---|---|---|---|---:|---:|---:|
| test | 20190925_111757_1_1 | `visible.mp4` | `infrared.mp4` | `visible.json`, `infrared.json` | 1000 | 1000 | visible=1000; infrared=1000 |
| test | 20190926_111509_1_7 | `visible.mp4` | `infrared.mp4` | `visible.json`, `infrared.json` | 1000 | 1000 | visible=1000; infrared=1000 |
| train | 20190925_205804_1_7 | `visible.mp4` | `infrared.mp4` | `visible.json`, `infrared.json` | 950 | 950 | visible=950; infrared=950 |
| train | 20190926_193515_1_6 | `visible.mp4` | `infrared.mp4` | `visible.json`, `infrared.json` | 1000 | 1000 | visible=1000; infrared=1000 |
| val | 20190926_200510_1_8 | `visible.mp4` | `infrared.mp4` | `visible.json`, `infrared.json` | 493 | 493 | visible=493; infrared=493 |

## Video Format

| sequence | modality | codec | resolution | fps | duration_sec | frame_count | decoded_sample_frames |
|---|---|---|---|---:|---:|---:|---|
| test/20190925_111757_1_1 | RGB/visible | mpeg4 | 1920x1080 | 20.0 | 50.0 | 1000 | 0, 500, 999 |
| test/20190925_111757_1_1 | IR/infrared | mpeg4 | 640x512 | 20.0 | 50.0 | 1000 | 0, 500, 999 |
| test/20190926_111509_1_7 | RGB/visible | mpeg4 | 1920x1080 | 20.0 | 50.0 | 1000 | 0, 500, 999 |
| test/20190926_111509_1_7 | IR/infrared | mpeg4 | 640x512 | 20.0 | 50.0 | 1000 | 0, 500, 999 |
| train/20190925_205804_1_7 | RGB/visible | mpeg4 | 1920x1080 | 20.0 | 47.5 | 950 | 0, 475, 949 |
| train/20190925_205804_1_7 | IR/infrared | mpeg4 | 640x512 | 20.0 | 47.5 | 950 | 0, 475, 949 |
| train/20190926_193515_1_6 | RGB/visible | mpeg4 | 1920x1080 | 20.0 | 50.0 | 1000 | 0, 500, 999 |
| train/20190926_193515_1_6 | IR/infrared | mpeg4 | 640x512 | 20.0 | 50.0 | 1000 | 0, 500, 999 |
| val/20190926_200510_1_8 | RGB/visible | mpeg4 | 1920x1080 | 20.0 | 24.65 | 493 | 0, 246, 492 |
| val/20190926_200510_1_8 | IR/infrared | mpeg4 | 640x512 | 20.0 | 24.65 | 493 | 0, 246, 492 |

## Annotation Structure

- Top-level type: dict
- Top-level keys observed: `exist`, `gt_rect`
- Target presence field: `exist`
- Bounding box field: `gt_rect`
- Bounding box format: `[x, y, w, h]` based on `gt_rect` values and image-dimension legality checks on sampled annotations.

| sequence | modality | records | present | absent | sampled refs valid | bbox valid/checked |
|---|---|---:|---:|---:|---:|---:|
| test/20190925_111757_1_1 | visible | 1000 | 1000 | 0 | 20 | 20/20 |
| test/20190925_111757_1_1 | infrared | 1000 | 1000 | 0 | 20 | 20/20 |
| test/20190926_111509_1_7 | visible | 1000 | 1000 | 0 | 20 | 20/20 |
| test/20190926_111509_1_7 | infrared | 1000 | 1000 | 0 | 20 | 20/20 |
| train/20190925_205804_1_7 | visible | 950 | 950 | 0 | 20 | 20/20 |
| train/20190925_205804_1_7 | infrared | 950 | 950 | 0 | 20 | 20/20 |
| train/20190926_193515_1_6 | visible | 1000 | 944 | 56 | 20 | 18/18 |
| train/20190926_193515_1_6 | infrared | 1000 | 1000 | 0 | 20 | 20/20 |
| val/20190926_200510_1_8 | visible | 493 | 474 | 19 | 20 | 19/19 |
| val/20190926_200510_1_8 | infrared | 493 | 479 | 14 | 20 | 19/19 |

## Full Dataset Lightweight Scan

- Total sequences: 318
- Split counts: test=91, train=160, val=67
- RGB present sequences: 318
- IR present sequences: 318
- Annotation present sequences: 318
- Complete RGB/IR/annotation sequences: 318

## Anomalies

- unreadable_rgb: 0
- unreadable_ir: 0
- annotation_parse_failure: 0
- missing_annotation: 0
- missing_rgb: 0
- missing_ir: 0
- frame_count_mismatch: 0
- missing_frame_pair: 0
- bbox_problem: 0
- unexpected_extension: 0

## Notes

- `infrared.mp4` is treated as IR because of official dataset structure and filenames, not because of visual appearance.
- Frame filename correspondence is not applicable because frames are stored inside MP4 containers rather than individual image files.
- Frame index correspondence means annotation list indices can be used against decoded video frame indices for the inspected sample.
- Strict RGB/IR synchronization is not tested in this step.
