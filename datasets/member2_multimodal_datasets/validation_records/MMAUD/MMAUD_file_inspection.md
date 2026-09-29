# MMAUD File Inspection

Dataset: MMAUD

Subset: UG2+ val

Original or Derived: DERIVED_SUBSET

Note: This report validates file presence, structure, and sampled readability only. It does not evaluate cross-modal synchronization.

## ARCHIVE

| Field | Value |
|---|---|
| Extraction | PASS |
| Extraction Root | samples/MMAUD/extracted/val |
| Data Root | samples/MMAUD/extracted/val/val |
| Extracted Size | 6,419,220,734 bytes |
| File Count | 5244 |
| Directory Count | 81 |
| Extension Distribution | .npy: 2818, .png: 2426 |
| Duplicate ZIP Paths | 0 |

First 4-level directory tree sample:

- `.`
- `val/`
- `val/seq0001/`
- `val/seq0001/Image/`
- `val/seq0001/lidar_360/`
- `val/seq0001/livox_avia/`
- `val/seq0001/radar_enhance_pcl/`
- `val/seq0002/`
- `val/seq0002/Image/`
- `val/seq0002/lidar_360/`
- `val/seq0002/livox_avia/`
- `val/seq0002/radar_enhance_pcl/`
- `val/seq0003/`
- `val/seq0003/Image/`
- `val/seq0003/lidar_360/`
- `val/seq0003/livox_avia/`
- `val/seq0003/radar_enhance_pcl/`
- `val/seq0004/`
- `val/seq0004/Image/`
- `val/seq0004/lidar_360/`
- `val/seq0004/livox_avia/`
- `val/seq0004/radar_enhance_pcl/`
- `val/seq0005/`
- `val/seq0005/Image/`
- `val/seq0005/lidar_360/`
- `val/seq0005/livox_avia/`
- `val/seq0005/radar_enhance_pcl/`
- `val/seq0006/`
- `val/seq0006/Image/`
- `val/seq0006/lidar_360/`
- `val/seq0006/livox_avia/`
- `val/seq0006/radar_enhance_pcl/`
- `val/seq0007/`
- `val/seq0007/Image/`
- `val/seq0007/lidar_360/`
- `val/seq0007/livox_avia/`
- `val/seq0007/radar_enhance_pcl/`
- `val/seq0008/`
- `val/seq0008/Image/`
- `val/seq0008/lidar_360/`
- `val/seq0008/livox_avia/`
- `val/seq0008/radar_enhance_pcl/`
- `val/seq0009/`
- `val/seq0009/Image/`
- `val/seq0009/lidar_360/`
- `val/seq0009/livox_avia/`
- `val/seq0009/radar_enhance_pcl/`
- `val/seq0010/`
- `val/seq0010/Image/`
- `val/seq0010/lidar_360/`
- `val/seq0010/livox_avia/`
- `val/seq0010/radar_enhance_pcl/`
- `val/seq0011/`
- `val/seq0011/Image/`
- `val/seq0011/lidar_360/`
- `val/seq0011/livox_avia/`
- `val/seq0011/radar_enhance_pcl/`
- `val/seq0012/`
- `val/seq0012/Image/`
- `val/seq0012/lidar_360/`
- `val/seq0012/livox_avia/`
- `val/seq0012/radar_enhance_pcl/`
- `val/seq0013/`
- `val/seq0013/Image/`
- `val/seq0013/lidar_360/`
- `val/seq0013/livox_avia/`
- `val/seq0013/radar_enhance_pcl/`
- `val/seq0014/`
- `val/seq0014/Image/`
- `val/seq0014/lidar_360/`
- `val/seq0014/livox_avia/`
- `val/seq0014/radar_enhance_pcl/`
- `val/seq0015/`
- `val/seq0015/Image/`
- `val/seq0015/lidar_360/`
- `val/seq0015/livox_avia/`
- `val/seq0015/radar_enhance_pcl/`
- `val/seq0016/`
- `val/seq0016/Image/`
- `val/seq0016/lidar_360/`
- `val/seq0016/livox_avia/`
- `val/seq0016/radar_enhance_pcl/`

## SEQUENCES

Sequence Count: 16

Sequence Names: seq0001, seq0002, seq0003, seq0004, seq0005, seq0006, seq0007, seq0008, seq0009, seq0010, seq0011, seq0012, seq0013, seq0014, seq0015, seq0016

| sequence | image | lidar_360 | livox_avia | radar | other |
|---|---|---|---|---|---|
| seq0001 | 147 | 50 | 50 | 74 | 0 |
| seq0002 | 151 | 51 | 51 | 76 | 0 |
| seq0003 | 153 | 51 | 51 | 76 | 0 |
| seq0004 | 157 | 52 | 52 | 78 | 0 |
| seq0005 | 150 | 51 | 50 | 76 | 0 |
| seq0006 | 150 | 50 | 50 | 75 | 0 |
| seq0007 | 150 | 50 | 50 | 75 | 0 |
| seq0008 | 148 | 50 | 50 | 75 | 0 |
| seq0009 | 151 | 49 | 50 | 75 | 0 |
| seq0010 | 149 | 50 | 50 | 74 | 0 |
| seq0011 | 152 | 51 | 51 | 75 | 0 |
| seq0012 | 153 | 51 | 51 | 77 | 0 |
| seq0013 | 150 | 50 | 50 | 75 | 0 |
| seq0014 | 153 | 51 | 51 | 77 | 0 |
| seq0015 | 157 | 52 | 52 | 79 | 0 |
| seq0016 | 155 | 35 | 51 | 77 | 0 |

## CAMERA

| Field | Value |
|---|---|
| Files Found | 2426 |
| Readable Samples | 9/9 |
| Format | PNG |
| Resolution | 2560x960 |
| Channels | 3 |
| Result | PASS |

| sequence | sample_file | format | resolution | channels | mode | dtype/bit-depth | read_status |
|---|---|---|---|---|---|---|---|
| seq0004 | samples/MMAUD/extracted/val/val/seq0004/Image/1706257437.055310.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0004 | samples/MMAUD/extracted/val/val/seq0004/Image/1706257438.587764.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0004 | samples/MMAUD/extracted/val/val/seq0004/Image/1706257441.055398.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0005 | samples/MMAUD/extracted/val/val/seq0005/Image/1706257442.387295.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0005 | samples/MMAUD/extracted/val/val/seq0005/Image/1706257443.887996.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0005 | samples/MMAUD/extracted/val/val/seq0005/Image/1706257446.523335.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0012 | samples/MMAUD/extracted/val/val/seq0012/Image/1706258284.548144.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0012 | samples/MMAUD/extracted/val/val/seq0012/Image/1706258285.615988.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |
| seq0012 | samples/MMAUD/extracted/val/val/seq0012/Image/1706258286.047883.png | PNG | 2560x960 | 3 | RGB | uint8 | PASS |

## LIDAR 360

| Field | Value |
|---|---|
| Files Found | 794 |
| Readable Samples | 5/5 |
| NPY Shape Examples | seq0002 [19968, 3] float64; seq0008 [19968, 3] float64; seq0011 [20064, 3] float64; seq0014 [19968, 3] float64; seq0016 [40032, 3] float64 |
| Result | PASS |

## LIVOX AVIA

| Field | Value |
|---|---|
| Files Found | 810 |
| Readable Samples | 5/5 |
| NPY Shape Examples | seq0001 [24000, 3] float64; seq0004 [24000, 3] float64; seq0009 [24000, 3] float64; seq0011 [24000, 3] float64; seq0012 [24000, 3] float64 |
| Result | PASS |

## RADAR

| Field | Value |
|---|---|
| Files Found | 1214 |
| Readable Samples | 5/5 |
| NPY Shape Examples | seq0003 [0] float64; seq0005 [0] float64; seq0010 [8, 3] float64; seq0012 [0] float64; seq0014 [0] float64 |
| Feature Semantics | FEATURE_SEMANTICS_UNKNOWN |
| Result | PASS |

## NPY SAMPLE DETAILS

| modality | sequence | file | shape | dtype | point_count | feature_dim | min | max | read_status |
|---|---|---|---|---|---|---|---|---|---|
| lidar_360 | seq0002 | samples/MMAUD/extracted/val/val/seq0002/lidar_360/1706255054.700092.npy | [19968, 3] | float64 | 19968 | 3 | -63.85300064086914 | 77.5260009765625 | PASS |
| lidar_360 | seq0008 | samples/MMAUD/extracted/val/val/seq0008/lidar_360/1706257659.900321.npy | [19968, 3] | float64 | 19968 | 3 | -63.86000061035156 | 77.56500244140625 | PASS |
| lidar_360 | seq0011 | samples/MMAUD/extracted/val/val/seq0011/lidar_360/1706258278.800170.npy | [20064, 3] | float64 | 20064 | 3 | -63.7869987487793 | 77.48799896240234 | PASS |
| lidar_360 | seq0014 | samples/MMAUD/extracted/val/val/seq0014/lidar_360/1706258742.700058.npy | [19968, 3] | float64 | 19968 | 3 | -63.757999420166016 | 49.7239990234375 | PASS |
| lidar_360 | seq0016 | samples/MMAUD/extracted/val/val/seq0016/lidar_360/1706256062.300752.npy | [40032, 3] | float64 | 40032 | 3 | -63.81999969482422 | 77.6510009765625 | PASS |
| livox_avia | seq0001 | samples/MMAUD/extracted/val/val/seq0001/livox_avia/1706255625.614195.npy | [24000, 3] | float64 | 24000 | 3 | -1.0420000553131104 | 20.591999053955078 | PASS |
| livox_avia | seq0004 | samples/MMAUD/extracted/val/val/seq0004/livox_avia/1706257440.201849.npy | [24000, 3] | float64 | 24000 | 3 | 0.0 | 0.0 | PASS |
| livox_avia | seq0009 | samples/MMAUD/extracted/val/val/seq0009/livox_avia/1706258172.697281.npy | [24000, 3] | float64 | 24000 | 3 | 0.0 | 0.0 | PASS |
| livox_avia | seq0011 | samples/MMAUD/extracted/val/val/seq0011/livox_avia/1706258281.397157.npy | [24000, 3] | float64 | 24000 | 3 | -159.19500732421875 | 370.0459899902344 | PASS |
| livox_avia | seq0012 | samples/MMAUD/extracted/val/val/seq0012/livox_avia/1706258284.897119.npy | [24000, 3] | float64 | 24000 | 3 | -245.32400512695312 | 387.18798828125 | PASS |
| radar_enhance_pcl | seq0003 | samples/MMAUD/extracted/val/val/seq0003/radar_enhance_pcl/1706257436.030265.npy | [0] | float64 | 0 | None | None | None | PASS |
| radar_enhance_pcl | seq0005 | samples/MMAUD/extracted/val/val/seq0005/radar_enhance_pcl/1706257444.963759.npy | [0] | float64 | 0 | None | None | None | PASS |
| radar_enhance_pcl | seq0010 | samples/MMAUD/extracted/val/val/seq0010/radar_enhance_pcl/1706258274.972275.npy | [8, 3] | float64 | 8 | 3 | -5.456375598907471 | 59.98753356933594 | PASS |
| radar_enhance_pcl | seq0012 | samples/MMAUD/extracted/val/val/seq0012/radar_enhance_pcl/1706258286.839188.npy | [0] | float64 | 0 | None | None | None | PASS |
| radar_enhance_pcl | seq0014 | samples/MMAUD/extracted/val/val/seq0014/radar_enhance_pcl/1706258743.444599.npy | [0] | float64 | 0 | None | None | None | PASS |

## TIMESTAMP

| modality | parse_status | timestamp_type | parsed | total | examples |
|---|---|---|---|---|---|
| Image | PASS | numeric_stem | 2426 | 2426 | 1706255621.570108, 1706255621.606015, 1706255621.638451, 1706255621.670069, 1706255621.706102 |
| lidar_360 | PASS | numeric_stem | 794 | 794 | 1706255621.600227, 1706255621.700287, 1706255621.800237, 1706255621.900150, 1706255622.000297 |
| livox_avia | PASS | numeric_stem | 810 | 810 | 1706255621.614239, 1706255621.714191, 1706255621.814266, 1706255621.914209, 1706255622.013213 |
| radar_enhance_pcl | PASS | numeric_stem | 1214 | 1214 | 1706255621.610851, 1706255621.677709, 1706255621.744115, 1706255621.811038, 1706255621.877650 |

No synchronization or nearest-timestamp matching was evaluated.

## ANOMALIES

| Field | Value |
|---|---|
| Empty Files | 0 |
| Unreadable Files | 0 |
| Unexpected Extensions | NONE |
| Small Files < 16 bytes | 0 |
| Duplicate ZIP Paths | 0 |

## SOURCE CONSISTENCY

| Item | Status |
|---|---|
| Camera | CONFIRMED_BY_SAMPLE |
| LiDAR | CONFIRMED_BY_SAMPLE |
| Radar | CONFIRMED_BY_SAMPLE |
| PNG | CONFIRMED_BY_SAMPLE |
| NPY | CONFIRMED_BY_SAMPLE |
| Sequence Structure | CONFIRMED_BY_SAMPLE |
| Timestamp Filenames | CONFIRMED_BY_SAMPLE |

## TECHNICAL RESULT

| Field | Value |
|---|---|
| FILE_STRUCTURE | PASS |
| FILE_READABILITY | PASS |
| TECHNICAL_VALIDATION | PASS |
| READY_FOR_CROSS_MODAL_VALIDATION | YES |
| note | This is file-level validation only; cross-modal synchronization has not been tested. |

