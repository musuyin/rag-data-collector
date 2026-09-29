# DroneRF Download Validation

Dataset: DroneRF  
Version: Mendeley Data v1  
Sample: Background + Parrot Bebop ON/Connected  
Stage: DOWNLOAD + SIZE + HASH + RAR INTEGRITY + CSV EXISTENCE  
Validation time: 2026-09-28T23:39:21.3282460+08:00

## Summary

Download: PASS  
Expected Total Size: 714,741,588 bytes  
Actual Total Size: 714,741,588 bytes  
Total Size Status: SIZE_MATCH  
RAR Open: PASS  
RAR Integrity: PASS  
RAR Integrity Method: `bsdtar -xO` streamed archive contents to null output; no files were extracted to disk.  
CSV Files Found: 82  
CSV Total Uncompressed Size: 7,816,289,911 bytes  
Ready For RF File Inspection: YES

## Background

### L File

Filename: RF Data_00000_L2.rar  
Role: BACKGROUND_L  
Expected Size: 162,435,106 bytes  
Actual Size: 162,435,106 bytes  
SHA256: c18ec4c0baa9628252abadc9919a4716102658e766cc1087e5dbc7f1d1e1c209  
RAR Open: PASS  
RAR Integrity: PASS  
Archive Entry Count: 21  
CSV Count: 20  
CSV Segment IDs: 21-40  
Detected Root Directory: RF Data_00000_L2  
CSV Name Pattern: 00000L_<segment_id>.csv  
CSV Uncompressed Size Range: 94,291,053 to 94,697,815 bytes  
CSV Total Uncompressed Size: 1,888,162,734 bytes

### H File

Filename: FR Data_00000_H2.rar  
Role: BACKGROUND_H  
Expected Size: 161,000,614 bytes  
Actual Size: 161,000,614 bytes  
SHA256: 976c9a818d6c58683b6e692554edd571529f06f1d12eababea9a206ceabbac74  
RAR Open: PASS  
RAR Integrity: PASS  
Archive Entry Count: 21  
CSV Count: 20  
CSV Segment IDs: 21-40  
Detected Root Directory: FR Data_00000_H2  
CSV Name Pattern: 00000H_<segment_id>.csv  
CSV Uncompressed Size Range: 94,244,414 to 94,454,917 bytes  
CSV Total Uncompressed Size: 1,886,399,598 bytes

Background Pair Structure: PASS  
Background Pair Segment Correspondence: L and H both contain segment IDs 21-40.

## Drone

Model: Parrot Bebop  
Mode: ON / Connected

### L File

Filename: RF Data_10000_L.rar  
Role: DRONE_L  
Expected Size: 217,760,401 bytes  
Actual Size: 217,760,401 bytes  
SHA256: 3fd15c79fa4a605fedb118748661861837e9ca186328d444d90731069f6d49fd  
RAR Open: PASS  
RAR Integrity: PASS  
Archive Entry Count: 22  
CSV Count: 21  
CSV Segment IDs: 0-20  
Detected Root Directory: RF Data_10000_L  
CSV Name Pattern: 10000L_<segment_id>.csv  
CSV Uncompressed Size Range: 95,707,106 to 102,991,383 bytes  
CSV Total Uncompressed Size: 2,057,039,087 bytes

### H File

Filename: RF Data_10000_H.rar  
Role: DRONE_H  
Expected Size: 173,545,467 bytes  
Actual Size: 173,545,467 bytes  
SHA256: 4d8e329f48d1c3b54847d976ff45f3babc5ca6a2a23178b06160387a4eeb2f12  
RAR Open: PASS  
RAR Integrity: PASS  
Archive Entry Count: 22  
CSV Count: 21  
CSV Segment IDs: 0-20  
Detected Root Directory: RF Data_10000_H  
CSV Name Pattern: 10000H_<segment_id>.csv  
CSV Uncompressed Size Range: 94,245,441 to 95,722,579 bytes  
CSV Total Uncompressed Size: 1,984,688,492 bytes

Drone Pair Structure: PASS  
Drone Pair Segment Correspondence: L and H both contain segment IDs 0-20.

## Scope Notes

No RAR archive was extracted to disk.  
No CSV content was parsed or analyzed.  
No FFT, STFT, spectrogram generation, filtering, classification, or model training was performed.  
Sample rate and physical L/H meaning were not inferred.  
Dataset Card final validation status was not modified.
