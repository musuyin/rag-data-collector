# Delivery Notes

## Raw Data Policy

Raw data remains in the local `samples/` directory and is not copied into this deliverable package.

Excluded from deliverables:

- Anti-UAV-RGBT.zip
- DroneRF RAR files
- DroneRF raw CSV files
- MMAUD val.zip
- MMAUD Camera files
- MMAUD LiDAR files
- MMAUD Radar files
- Anti-UAV300 videos and extracted annotation JSON files

## Reasons

- Storage Cost: raw files are large and not needed for a report deliverable.
- License Restrictions: redistribution rights are dataset-specific and not always confirmed.
- Redistribution Risk: Anti-UAV300 license remains RISK.
- Reproducibility: metadata, hash, source URL, manifests, and validation records are sufficient for another member to re-acquire official data when needed.

## Reproducibility

Anyone who needs to reproduce validation should use:

- `source_manifest.csv`
- dataset-specific `download_manifest.json`
- SHA256 values
- official source URLs
- validation records under `validation_records/`

This package is a validation deliverable, not a raw dataset redistribution package.
