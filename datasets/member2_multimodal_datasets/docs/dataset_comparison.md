# Dataset Comparison

| Dataset | Modality | Association Key | Association Level | Technical Validation | Cross-Modal Validation | License | Readiness | Main Advantage | Main Limitation |
|---|---|---|---|---|---|---|---|---|---|
| MMAUD | Camera; LiDAR; Radar | sequence_id + timestamp | Timestamp-Level Association | PASS | PARTIAL | CC BY-NC-SA 4.0; non-commercial by default | CROSS_MODAL_READY | Multi-sensor heterogeneous UAV data | Calibration / Audio / strict sync not fully validated |
| Anti-UAV300 | RGB / Visible; Thermal / Infrared | sequence_id + frame_index | Frame-Level Pairing | PASS | PASS | RISK | CROSS_MODAL_READY | RGB-T frame-level pairing across 318/318 sequences | License risk + no hard synchronization evidence |
| DroneRF | Raw RF | filename/BUI + segment_id | Semantic Entity Association | PASS | PASS at semantic RF label level | CC BY 4.0 | BASIC_USABLE | Strong RF to drone model / operating mode association | Not a synchronized visual-RF multimodal dataset |

## Interpretation

MMAUD is the strongest fit for heterogeneous sensor storage and timestamp association. Anti-UAV300 is the strongest fit for RGB-T frame-level pairing. DroneRF is the strongest fit for RF knowledge indexing, model/mode labels, and semantic association.
