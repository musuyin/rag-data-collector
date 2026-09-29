# MMAUD Final Validation Report

## 1. Dataset Overview

MMAUD is an official multimodal anti-UAV dataset associated with NTU / ARIS and an ICRA 2024 paper. This final evaluation combines source audit, sample download, file inspection, and cross-modal timestamp validation already completed in this project.

Final dataset status: `PARTIALLY_VERIFIED`  
Project readiness: `CROSS_MODAL_READY`

The result is intentionally conservative: real sensor data was validated, but only for a UG2+ derived validation subset, not for every original MMAUD V1/V2/V3 package.

## 2. Official Sources

| Evidence Type | Status | Notes |
|---|---|---|
| Official dataset page | PASS | https://ntu-aris.github.io/MMAUD/ |
| Official paper | PASS | https://arxiv.org/abs/2402.03706 |
| Official repository | PASS | https://github.com/ntu-aris/MMAUD |
| Official/challenge download entry | PASS | MMAUD official downloads and UG2+ Track 5 sources were recorded in the source audit and sample candidate reports. |
| License | PASS | CC BY-NC-SA 4.0 for dataset/work; MIT repository license recorded separately for site/code. |

`SOURCE_VALIDATION: PASS`

## 3. Data Scale

| Scope | Value |
|---|---|
| Official Dataset | MMAUD |
| Official visible V1 size | 72.5 GB across visible V1 rows; full V1/V2/V3 total UNKNOWN |
| Official sequence count | 50 sequences documented by paper |
| Official duration | Over 1700 seconds documented by paper |
| Validated Subset | UG2+ / V2-V3 validation subset |
| Subset Type | DERIVED_SUBSET |
| Downloaded Archive | val.zip |
| Archive Size | 5,325,448,505 bytes |
| Extracted Size | 6,419,220,734 bytes |
| File Count | 5244 |
| Sequence Count | 16 |

The validated subset must not be treated as complete MMAUD validation.

## 4. Validated Sample

The validated sample is `val.zip`, a UG2+ / V2-V3 validation derived subset. It contains 16 sequences with Camera, LiDAR360, Livox Avia, and Radar directories. The ZIP archive opened, integrity testing passed, extraction succeeded, and sampled PNG/NPY readability passed.

## 5. Modalities

| Modality | Official MMAUD | Present in Validated Sample | Technical Validation | Cross-Modal Validation | Notes |
|---|---|---|---|---|---|
| RGB / Camera | YES | YES | PASS | PASS | PNG camera files are present in all 16 validated sequences; sampled PNG readability passed; filename timestamps support nearest-neighbor matching. |
| Audio | YES | NO | NOT_TESTED | NOT_TESTED | Audio is documented in official MMAUD but is not present in the current val.zip derived validation subset. |
| Radar | YES | YES | PASS | PASS | radar_enhance_pcl NPY files are present; sampled readability passed; Camera-to-Radar median nearest-timestamp delta is 17.367 ms. |
| LiDAR360 | YES | YES | PASS | PASS | lidar_360 NPY files are present; sampled readability passed; Camera-to-LiDAR360 median nearest-timestamp delta is 20.182 ms. |
| Livox Avia | YES | YES | PASS | PASS | livox_avia NPY files are present; sampled readability passed; Camera-to-Livox median nearest-timestamp delta is 18.995 ms. |
| Trajectory / Ground Truth | YES | NO | NOT_TESTED | NOT_TESTED | Official MMAUD and UG2+ references mention Leica/pose/ground truth, but the downloaded val.zip input subset did not include ground_truth or pose/reference CSV files. |
| RF | NO | NO | NOT_TESTED | NOT_TESTED | Official paper comparison/source audit indicates RF/IQ is not included. |
| IR | NO | NO | NOT_TESTED | NOT_TESTED | Thermal/IR is not listed in official sensors and was not found in the validated subset. |

## 6. Formats

| Format / Structure | OFFICIAL_DOCUMENTED | CONFIRMED_BY_SAMPLE | Notes |
|---|---|---|---|
| PNG | YES | YES | 2,426 .png camera files; sampled images read as 2560x960 RGB PNG. |
| NPY | YES | YES | 2,818 .npy files across lidar_360, livox_avia, and radar_enhance_pcl; sampled NPY arrays were readable. |
| Directory structure | YES | YES | val/seq0001..seq0016 with Image, lidar_360, livox_avia, radar_enhance_pcl. |
| Timestamp-style filenames | YES | YES | All inspected modality filenames parse as numeric timestamp stems. |
| ROSBag | YES | NO | Documented for official full MMAUD, but no ROSBag was read in this val.zip subset. |
| PCD | YES | NO | Documented for full filesystem exports, but current val.zip confirmed NPY point-cloud-like arrays, not PCD files. |

ROSBag, PCD, audio NPY exports, and ground-truth bag/numpy files remain official-documented where supported by sources, but they were not confirmed by this `val.zip` sample unless listed as `CONFIRMED_BY_SAMPLE = YES` above.

## 7. Labels / Ground Truth

| Item | Status | Notes |
|---|---|---|
| 2D annotation | NOT_TESTED | MMAUD_2D.zip was not downloaded; current val.zip contains sensor inputs, not 2D labels. |
| Ground Truth | NOT_TESTED | No ground_truth directory or Leica/pose file was found in the validated val.zip subset. |
| Pose / Reference CSV | NOT_TESTED | No local UG2+ reference/pose CSV matching this val subset was available during final validation. |
| Timestamp | PASS | All camera, lidar_360, livox_avia, and radar filenames parsed as numeric timestamps. |
| Sequence ID | PASS | 16 sequence directories were confirmed: seq0001 through seq0016. |
| Drone Model | NOT_TESTED | Official sources document drone models, but the current subset did not expose per-file drone model labels. |
| Environment Label | NOT_TESTED | Official sources document environment categories, but the current subset did not expose per-sequence environment labels. |

Annotation validation is `PARTIAL`: timestamp and sequence identifiers were verified, but 2D annotation files, local ground truth, pose/reference CSV, drone model labels, and environment labels were not validated in this subset.

## 8. Collection Environment

Official sources document outdoor collection, V1 rooftop simple settings, V2/V3 carpark hard/moderate settings, no night/rain conditions, and altitude/range context. The current subset does not independently expose per-sequence environment metadata, so collection environment validation is `PARTIAL`.

## 9. Sensor Parameters

Official sources document Pixel-XYZ cameras, Livox Avia, Livox Mid360, Hikvision audio arrays, Oculii Eagle ETH04 radar, and Leica Nova MS60 ground truth. The sample confirmed Camera PNG dimensions and NPY point-cloud-like data for LiDAR/Radar. Audio, local calibration files, and Leica ground-truth files were not validated in this subset, so sensor parameter validation is `PARTIAL`.

## 10. Technical Validation

| Metric | Result |
|---|---|
| Extraction Status | PASS |
| Extracted Size | 6,419,220,734 bytes |
| File Count | 5244 |
| Directory Count | 81 |
| Sequence Count | 16 |
| Camera Readability | PASS |
| LiDAR360 Readability | PASS |
| Livox Avia Readability | PASS |
| Radar Readability | PASS |
| Timestamp Parse Status | PASS |
| Technical Validation | PASS |

## 11. Cross-Modal Validation

| Metric | Result |
|---|---|
| Sequence-Level Association | PASS |
| Timestamp Association | PASS |
| Camera ? LiDAR360 Median Delta | 20.182 ms |
| Camera ? Livox Avia Median Delta | 18.995 ms |
| Camera ? Radar Median Delta | 17.367 ms |
| Calibration | PARTIAL |
| Synchronization | LIKELY_SYNCHRONIZED |
| Association Strength | MEDIUM |
| Cross-Modal Index Feasible | YES |
| Cross-Modal Validation | PARTIAL |

Interpretation: sequence-level and timestamp-level association are good enough for a practical cross-modal index. `LIKELY_SYNCHRONIZED` does not mean `SYNCHRONIZED_CONFIRMED`, and `MEDIUM` association strength reflects partial local calibration/reference support.

## 12. Cross-Modal Index Feasibility

A future unified index structure is feasible:

```json
{
  "dataset": "MMAUD",
  "subset": "UG2_val",
  "sequence_id": "seqXXXX",
  "camera": {"timestamp": "...", "file": "..."},
  "lidar360": {"timestamp": "...", "file": "...", "delta_ms": "..."},
  "livox_avia": {"timestamp": "...", "file": "...", "delta_ms": "..."},
  "radar": {"timestamp": "...", "file": "...", "delta_ms": "..."}
}
```

Reason: all validated modalities share sequence directories, all filenames expose parseable timestamps, and nearest-neighbor matching yields practical deltas. This report does not bulk-generate those records.

## 13. License

`LICENSE_VALIDATION: PASS`

MMAUD dataset/work licensing is CC BY-NC-SA 4.0. It supports non-commercial academic research with attribution and share-alike requirements. Commercial use is not allowed by default and requires contacting the authors. The repository MIT license applies to site/code and is tracked separately.

## 14. Limitations

- The validated data is a UG2+ derived validation subset, not the complete MMAUD V1/V2/V3 dataset.
- Audio is documented by official MMAUD sources but was not present in the downloaded val.zip subset and remains NOT_TESTED.
- Calibration/reference support is PARTIAL: official/source-level calibration resources are documented, but no local calibration matrices or transforms were validated inside val.zip.
- Cross-modal validation is based on sequence_id plus nearest-neighbor timestamp matching, not strict hardware-level synchronization.
- Sensor rates differ across modalities, so one-to-one frame correspondence must not be assumed.
- Ground truth, pose/reference CSV, and 2D annotations were not validated in the downloaded val.zip subset.
- Complete V1/V2/V3 packages were not exhaustively downloaded or validated.
- Dataset/work license is CC BY-NC-SA 4.0, so commercial use is not allowed by default.

## 15. Recommended Uses

- Multimodal data storage research
- Cross-modal indexing using sequence_id plus timestamp metadata
- Camera-to-LiDAR and Camera-to-Radar lookup experiments
- Multi-sensor temporal association studies
- UAV knowledge-base prototyping
- Multimodal retrieval system preparation
- Future embedding experiments after an explicit downstream embedding stage

Not yet proven by this validation:

- Image-to-Audio retrieval, because Audio was not present in the validated subset.
- Ground-truth pose evaluation, because local pose/reference CSV or ground_truth files were not validated.
- Strict hardware synchronization claims, because current validation supports likely timestamp association rather than confirmed hardware sync.

## 16. Final Verdict

| Item | Result |
|---|---|
| Source Validation | PASS |
| Technical Validation | PASS |
| Annotation Validation | PARTIAL |
| Cross-Modal Validation | PARTIAL |
| License Validation | PASS |
| Collection Environment Validation | PARTIAL |
| Sensor Parameter Validation | PARTIAL |
| Dataset Status | PARTIALLY_VERIFIED |
| Project Readiness | CROSS_MODAL_READY |

Final decision: `PARTIALLY_VERIFIED`.

MMAUD is suitable for this project's cross-modal knowledge-management direction because real Camera, LiDAR360, Livox Avia, and Radar files from an official-related derived validation subset were downloaded, inspected, and associated by sequence and timestamp. It is not marked `VERIFIED` because Audio, local calibration/reference assets, local ground truth/pose CSV, 2D annotations, and complete V1/V2/V3 coverage remain incomplete.
