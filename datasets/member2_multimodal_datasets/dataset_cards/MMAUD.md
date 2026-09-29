# MMAUD Dataset Card

Last checked: 2026-09-23  
Download performed: YES, for `val.zip` only  
Dataset Status: PARTIALLY_VERIFIED  
Project Readiness: CROSS_MODAL_READY

## Basic Information

| Field | Value |
|---|---|
| dataset_id | MMAUD |
| dataset_name | MMAUD |
| full_name | CONFLICT |
| version | V1; V2; V3 |
| organization | Nanyang Technological University (NTU), School of Electrical and Electronic Engineering / ARIS |
| publication_year | 2024 |
| official_url | https://ntu-aris.github.io/MMAUD/ |
| repository_url | https://github.com/ntu-aris/MMAUD |
| paper_url | https://arxiv.org/abs/2402.03706 |
| download_url | https://ntu-aris.github.io/MMAUD/#downloads |

## Validation Summary

| Item | Status |
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

Source validation is `PASS`: the official dataset page, official paper, official repository, official/challenge download entries, and license evidence are present. The final dataset status is not `VERIFIED` because this run validated a derived subset rather than the full MMAUD V1/V2/V3 dataset, and several modalities/assets remain untested.

## Validated Subset

| Field | Value |
|---|---|
| Official Dataset | MMAUD |
| Validated Subset | UG2+ / V2-V3 validation subset |
| Subset Type | DERIVED_SUBSET |
| Downloaded Archive | val.zip |
| Archive Size | 5,325,448,505 bytes |
| Extracted Size | 6,419,220,734 bytes |
| File Count | 5244 |
| Sequence Count | 16 |
| Data Root | samples/MMAUD/extracted/val/val |

This validation does not claim that complete MMAUD was exhaustively validated.

## Data Scale

Official full MMAUD scale and validated subset scale are intentionally separated.

| Scope | Scale |
|---|---|
| Official MMAUD | V1 visible rows total 72.5 GB; full V1/V2/V3 total UNKNOWN |
| Official sequence count | 50 |
| Official duration | paper: over 1700 seconds; V1 visible rows total 1525.5 seconds; V2/V3 durations UNKNOWN |
| Validated subset archive | 5,325,448,505 bytes |
| Validated subset extracted size | 6,419,220,734 bytes |
| Validated subset files | 5244 |
| Validated subset sequences | 16 |

## Modalities

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

## Formats

| Format / Structure | OFFICIAL_DOCUMENTED | CONFIRMED_BY_SAMPLE | Notes |
|---|---|---|---|
| PNG | YES | YES | 2,426 .png camera files; sampled images read as 2560x960 RGB PNG. |
| NPY | YES | YES | 2,818 .npy files across lidar_360, livox_avia, and radar_enhance_pcl; sampled NPY arrays were readable. |
| Directory structure | YES | YES | val/seq0001..seq0016 with Image, lidar_360, livox_avia, radar_enhance_pcl. |
| Timestamp-style filenames | YES | YES | All inspected modality filenames parse as numeric timestamp stems. |
| ROSBag | YES | NO | Documented for official full MMAUD, but no ROSBag was read in this val.zip subset. |
| PCD | YES | NO | Documented for full filesystem exports, but current val.zip confirmed NPY point-cloud-like arrays, not PCD files. |

## Labels / Ground Truth

| Item | Status | Notes |
|---|---|---|
| 2D annotation | NOT_TESTED | MMAUD_2D.zip was not downloaded; current val.zip contains sensor inputs, not 2D labels. |
| Ground Truth | NOT_TESTED | No ground_truth directory or Leica/pose file was found in the validated val.zip subset. |
| Pose / Reference CSV | NOT_TESTED | No local UG2+ reference/pose CSV matching this val subset was available during final validation. |
| Timestamp | PASS | All camera, lidar_360, livox_avia, and radar filenames parsed as numeric timestamps. |
| Sequence ID | PASS | 16 sequence directories were confirmed: seq0001 through seq0016. |
| Drone Model | NOT_TESTED | Official sources document drone models, but the current subset did not expose per-file drone model labels. |
| Environment Label | NOT_TESTED | Official sources document environment categories, but the current subset did not expose per-sequence environment labels. |

## Collection Environment

Official documentation supports outdoor rooftop/carpark MMAUD collection context, including V1 rooftop simple and V2/V3 carpark hard/moderate. The validated `val.zip` subset did not include independent per-sequence environment label files, so collection-environment validation remains `PARTIAL`.

## Sensor Parameters

Sensor parameters are documented by official sources for camera, audio, radar, LiDAR, and Leica ground truth. The validated subset confirmed actual camera PNG dimensions and NPY-based radar/LiDAR-style files, but did not locally validate calibration matrices, audio exports, or Leica ground truth files. Sensor parameter validation is therefore `PARTIAL`.

## Technical Validation

| Metric | Result |
|---|---|
| Extraction | PASS |
| File Structure | PASS |
| File Readability | PASS |
| Technical Validation | PASS |
| Camera Readability | PASS |
| LiDAR360 Readability | PASS |
| Livox Avia Readability | PASS |
| Radar Readability | PASS |
| Timestamp Parse Status | PASS |

## Cross-Modal Validation

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

Current evidence supports a `sequence_id + timestamp` cross-modal index. It does not prove strict hardware synchronization, and it does not imply every Camera frame has a unique perfectly simultaneous Radar or LiDAR sample.

## Cross-Modal Index Feasibility

`CROSS_MODAL_INDEX_FEASIBLE = YES` because each validated sequence contains Camera, LiDAR360, Livox Avia, and Radar directories; filenames parse as timestamps; and nearest-neighbor timestamp matching produced practical deltas across all validated sequences. A future record can use fields such as dataset, subset, sequence_id, camera timestamp/file, nearest lidar/radar file, and delta_ms. This card does not bulk-generate those records.

## License

Dataset/work license: CC BY-NC-SA 4.0. Research/non-commercial use is supported, redistribution/adaptation are allowed under BY-NC-SA terms, commercial use is not allowed by default, and citation is required. The GitHub repository MIT license is recorded separately for site/code and does not replace the dataset/work license.

## Advantages

- Official page, paper, repository, challenge page, and license evidence are available.
- Validated real subset contains Camera, Radar, LiDAR360, and Livox Avia data in a clear sequence structure.
- PNG and NPY files were actually read in samples, not only documented.
- Timestamp-style filenames are parseable across all validated modalities.
- Nearest-timestamp matching produced practical median deltas: 20.182 ms Camera-LiDAR360, 18.995 ms Camera-Livox, and 17.367 ms Camera-Radar.
- A sequence_id + timestamp cross-modal index is technically feasible for knowledge-management and retrieval experiments.

## Limitations

- The validated data is a UG2+ derived validation subset, not the complete MMAUD V1/V2/V3 dataset.
- Audio is documented by official MMAUD sources but was not present in the downloaded val.zip subset and remains NOT_TESTED.
- Calibration/reference support is PARTIAL: official/source-level calibration resources are documented, but no local calibration matrices or transforms were validated inside val.zip.
- Cross-modal validation is based on sequence_id plus nearest-neighbor timestamp matching, not strict hardware-level synchronization.
- Sensor rates differ across modalities, so one-to-one frame correspondence must not be assumed.
- Ground truth, pose/reference CSV, and 2D annotations were not validated in the downloaded val.zip subset.
- Complete V1/V2/V3 packages were not exhaustively downloaded or validated.
- Dataset/work license is CC BY-NC-SA 4.0, so commercial use is not allowed by default.

## Recommended Uses

- Multimodal data storage research
- Cross-modal indexing using sequence_id plus timestamp metadata
- Camera-to-LiDAR and Camera-to-Radar lookup experiments
- Multi-sensor temporal association studies
- UAV knowledge-base prototyping
- Multimodal retrieval system preparation
- Future embedding experiments after an explicit downstream embedding stage

Current validation does not prove:

- Image-to-Audio retrieval, because Audio was not present in the validated subset.
- Ground-truth pose evaluation, because local pose/reference CSV or ground_truth files were not validated.
- Strict hardware synchronization claims, because current validation supports likely timestamp association rather than confirmed hardware sync.

## Sources

| Source | Type | Evidence |
|---|---|---|
| https://ntu-aris.github.io/MMAUD/ | Level 1 official dataset page | Official MMAUD project page with dataset overview, sensor summary, downloads, calibration link, 2D baseline link, citation, and licence. |
| https://github.com/ntu-aris/MMAUD | Level 1 official GitHub repository | Official repository backing the GitHub Pages dataset site. |
| https://arxiv.org/abs/2402.03706 | Level 2 original paper | Original MMAUD paper accepted by ICRA 2024. |
| https://arxiv.org/html/2402.03706 | Level 2 original paper HTML | Paper text used for sensor setup, dataset format, sequence count, split, and synchronization limitations. |
| https://cvpr2024ug2challenge.github.io/dataset24_t5.html | official UG2 challenge page | Official challenge page describing an MMAUD-based track with fisheye images, radar, LiDAR, Leica ground truth, and training/validation sequence counts. |
| https://creativecommons.org/licenses/by-nc-sa/4.0/ | license deed | Used to verify explicit Share/Adapt permissions and NonCommercial/ShareAlike terms. |
| https://raw.githubusercontent.com/ntu-aris/MMAUD/gh-pages/LICENSE | official GitHub repository LICENSE file | MIT license file for repository/site code, recorded separately from dataset/work license. |
