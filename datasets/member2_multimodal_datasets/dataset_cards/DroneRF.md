# DroneRF Dataset Card

Last checked: 2026-09-29  
Status: VERIFIED  
Download performed: YES_SELECTED_SUBSET_ONLY

## Basic Information

| Field | Value |
|---|---|
| dataset_id | DroneRF |
| dataset_name | DroneRF |
| full_name | DroneRF dataset: A dataset of drones for RF-based detection, classification, and identification |
| version | Mendeley Data v1 |
| official_url | https://data.mendeley.com/datasets/f4c2b4n755/1 |
| dataset_repository | https://data.mendeley.com/datasets/f4c2b4n755/1 |
| repository_url | https://github.com/Al-Sad/DroneRF |
| paper_url | https://doi.org/10.1016/j.dib.2019.104313 |
| related_research_paper_url | https://doi.org/10.1016/j.future.2019.05.007 |
| dataset_doi | 10.17632/f4c2b4n755.1 |
| organization | Qatar University; Tampere affiliation for one author in the data article |
| publication_year | 2019 |

## Modalities

| Modality | Status |
|---|---|
| RGB Image | NO |
| RGB Video | NO |
| Thermal / IR | NO |
| Audio | NO |
| RF | YES |
| Radar | NO |
| LiDAR | NO |
| Event Camera | NO |
| Trajectory | NO |
| Flight Log | NO |
| Telemetry | NO |
| GPS | NO |
| IMU | NO |
| Text Metadata | YES |

PRIMARY_MODALITY: RF  
SECONDARY_MODALITY: TEXT_METADATA

## Data Scale

| Field | Value |
|---|---|
| total_size | over 40GB according to original Data in Brief article; exact bytes UNKNOWN |
| number_of_segments | 227 |
| number_of_files | 454 CSV record files by article statement |
| number_of_samples | 4,540 x 10^6 raw samples by published table totals |
| drone_model_count | 3 plus no-drone/background condition |
| operating_modes | OFF/background; on and connected; hovering; flying; video recording |
| duration | 10.25s background and approximately 5.25s per flight mode; total summed duration UNKNOWN |
| split | no fixed official train/validation/test split confirmed; related code uses 10-fold cross-validation |

## Drone Models

| Class | Source-Level Detail |
|---|---|
| No Drone | RF background activities |
| Parrot Bebop | BUI group 10000-10011 in official MATLAB code |
| Parrot AR Drone | BUI group 10100-10111 in official MATLAB code |
| DJI Phantom | BUI group 11000 in official MATLAB code; paper references Phantom 3 Standard |

## Operating Modes

| Mode | Status |
|---|---|
| OFF / background | YES |
| ON / connected | YES |
| Hovering | YES |
| Flying without video recording | YES |
| Flying with video recording | YES |

Labels are source-level real labels encoded through BUI/filename conventions and official labeling scripts, not standalone annotation JSON files.

## RF Representation

| Field | Value |
|---|---|
| RAW_RF_AVAILABLE | YES |
| IQ_AVAILABLE | NO |
| SPECTRUM_AVAILABLE | NO |
| SPECTROGRAM_AVAILABLE | NO |
| stored representation | time-domain amplitude samples of acquired raw RF signals |
| raw file format | CSV |
| derived formats from official code | MAT and processed RF_Data.csv |

The RF receiver hardware has I/Q-related specifications, but the public dataset is described as amplitude samples in CSV files. Frequency-domain spectra can be calculated with DFT/FFT; they are not confirmed as stored raw dataset files.

## Acquisition Parameters

| Parameter | Value |
|---|---|
| receiver_model | National Instruments USRP-2943 / NI-USRP2943R |
| antenna | UNKNOWN |
| receiver_frequency_range | 1.2GHz-6GHz hardware specification |
| experiment_frequency | WiFi 2.4GHz assumption in the paper |
| bandwidth | 40MHz maximum instantaneous bandwidth per receiver; two receivers capture lower/upper halves of an 80MHz spectrum |
| sample_rate | UNKNOWN for stored files; hardware maximum I/Q sample rate is 200 MS/s |
| channels | 2 channels in receiver specification; two receivers used for lower/upper spectrum halves |
| ADC | 14-bit |
| environment | laboratory setting, Qatar University, Doha |
| distance / line_of_sight / interference | UNKNOWN |

## Labels / Metadata

| Field | Value |
|---|---|
| label_source | FILENAME / BUI plus official labeling scripts |
| drone/no-drone | YES |
| drone model | YES |
| operating mode | YES_SOURCE_LEVEL |
| frequency band | YES via L/H filename component |
| recording id | YES via segment number in filename |
| timestamp | NO_CONFIRMED |
| session id | UNKNOWN |
| standalone annotation JSON | NO_CONFIRMED |

## RF Association

| Field | Value |
|---|---|
| RF_MODEL_ASSOCIATION | STRONG |
| RF_MODE_ASSOCIATION | STRONG |
| RF_RECORDING_SESSION_ASSOCIATION | MEDIUM |
| multimodal association strength | WEAK |

DroneRF's project value is not synchronized multimodal fusion. Its value is RF modality coverage with strong source-level links from RF files to drone/no-drone, drone model, and operating-mode labels.

## Download Structure

| Field | Value |
|---|---|
| official download | Mendeley Data v1 |
| complete dataset download | YES via Download All button |
| package_size | official full dataset over 40GB; selected validation subset 714,741,588 bytes compressed and 7,816,289,911 bytes extracted |
| file_count | 454 CSV record files in official full dataset by article; selected validation subset contains 82 extracted CSV files |
| single_file_download | YES for official Mendeley RAR file objects used in this validation; individual CSV direct download remains NO_CONFIRMED |
| per_drone_download | PARTIAL via official Mendeley RAR file objects; selected Bebop ON/Connected RAR pair validated |
| per_mode_download | PARTIAL via official Mendeley RAR file objects; selected Bebop ON/Connected RAR pair validated |
| partial_download_supported | YES_OFFICIAL_RAR_OBJECTS; NO_CONFIRMED_INDIVIDUAL_CSV |
| small_sample_available | YES_OFFICIAL_SELECTED_RAW_RF_SUBSET |

Validation was performed on an official selected raw RF subset, not the full >40GB dataset.

## Validated Sample

| Component | Value |
|---|---|
| source | Official Mendeley Data v1 RAR file objects |
| compressed files | 4 |
| compressed total size | 714,741,588 bytes |
| extracted CSV count | 82 |
| extracted total size | 7,816,289,911 bytes |
| background sample | 20 L + 20 H CSV; BUI `00000`; segments 21-40 |
| drone sample | 21 L + 21 H CSV; BUI `10000`; Parrot Bebop ON / Connected; segments 0-20 |
| scope | selected official raw RF subset only; full dataset was not exhaustively inspected |

Validated sample reports:

| Report | Purpose |
|---|---|
| `samples/DroneRF/download_manifest.json` | download, size, SHA-256, RAR structure |
| `validation/DroneRF_download_validation.json` | download-stage validation |
| `validation/DroneRF_file_inspection.json` | extracted CSV and RF technical validation |

## License

| Field | Value |
|---|---|
| dataset_license | CC BY 4.0 |
| research_use | YES |
| commercial_use | YES under CC BY 4.0 terms unless platform terms add restrictions |
| redistribution | YES with attribution |
| modification | YES with attribution |
| citation_required | YES |
| registration_required | UNKNOWN |
| code_license | Apache-2.0 for official code repository |
| license_status | PASS |

## Validation Summary

| Field | Value |
|---|---|
| source_validation | PASS |
| technical_validation | PASS |
| label_validation | PASS |
| rf_structure_validation | PASS |
| license_validation | PASS |
| collection_environment_validation | PARTIAL |
| sensor_parameter_validation | PARTIAL |
| annotation_validation | PASS_FILENAME_BUI_LABELS |
| cross_modal_validation | NOT_APPLICABLE_RF_SINGLE_MODALITY |
| dataset_status | VERIFIED |
| project_readiness | BASIC_USABLE |
| raw_rf_available | YES |
| iq_available | NO |
| spectrum_available | NO |
| spectrogram_available | NO |
| RAW_RF | PASS |
| CSV_READABILITY | PASS |
| NUMERIC_PARSE | PASS |
| L_H_PAIRING | PASS |
| SEGMENT_STRUCTURE | PASS |
| FILENAME_PARSE | PASS |
| BACKGROUND_LABEL_VALIDATION | PASS |
| DRONE_MODEL_LABEL_VALIDATION | PASS |
| OPERATING_MODE_LABEL_VALIDATION | PASS |
| RF_MODEL_ASSOCIATION | STRONG |
| RF_MODE_ASSOCIATION | STRONG |
| RF_KNOWLEDGE_INDEX_FEASIBLE | YES |
| SAMPLE_RATE | UNKNOWN |
| L_H_PHYSICAL_SEMANTICS | TWO_PART_SEGMENT_PAIR_CONFIRMED; EXACT_PHYSICAL_SEMANTICS_UNKNOWN |

`VERIFIED` here means the project-relevant RF data structure, label association, and file readability passed validation on an official selected raw RF subset. It does not mean every file in the full >40GB dataset was inspected.

## Project Readiness

PROJECT_READINESS: BASIC_USABLE

DroneRF is not a synchronized multimodal sensor dataset, so it should not be marked `CROSS_MODAL_READY`. It is a high-value RF modality source with strong entity/mode association. Its value for the broader UAV multimodal knowledge system is knowledge-level association:

```text
Drone Entity -> RF Representation
Drone Entity -> Operating Mode -> RF Samples
```

This is KNOWLEDGE-LEVEL CROSS-MODAL ASSOCIATION, not SENSOR-LEVEL SYNCHRONIZATION.

## Knowledge Index Feasibility

RF_KNOWLEDGE_INDEX_FEASIBLE: YES

The validated structure supports records shaped like:

```json
{
  "dataset": "DroneRF",
  "segment_id": 0,
  "drone_model": "Parrot Bebop",
  "operating_mode": "ON/Connected",
  "rf": {
    "L_file": "10000L_0.csv",
    "H_file": "10000H_0.csv"
  }
}
```

## Recommended Uses

| Use | Status |
|---|---|
| RF data storage | VALIDATED_FUNCTION |
| RF metadata indexing | VALIDATED_FUNCTION |
| Drone model -> RF retrieval | VALIDATED_FUNCTION |
| Operating mode -> RF retrieval | VALIDATED_FUNCTION |
| RF knowledge graph | VALIDATED_FUNCTION |
| Multimodal knowledge system | VALIDATED_FUNCTION at knowledge layer |
| RF feature extraction experiments | FUTURE_USE |
| Spectrogram generation | FUTURE_USE |
| RF embedding experiments | FUTURE_USE |
| Classification experiments | FUTURE_USE |

## Limitations

| Limitation | Status |
|---|---|
| stored sample rate | UNKNOWN |
| exact L/H physical semantics | UNKNOWN |
| full >40GB dataset inspection | NOT_DONE |
| synchronized RGB / audio / radar / LiDAR | NOT_AVAILABLE |
| sensor-level cross-modal synchronization | NOT_APPLICABLE |
| FFT / STFT / spectrogram validation | NOT_DONE |
| embedding / model training / classification validation | NOT_DONE |

## Sources

| Source | Type | Evidence |
|---|---|---|
| https://data.mendeley.com/datasets/f4c2b4n755/1 | official Mendeley Data page | Dataset identity, DOI, v1, authors, description, license |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC6727013/ | original Data in Brief full text | Data scale, format, labels, environment, receiver setup |
| https://tuhat.helsinki.fi/ws/portalfiles/portal/174931254/1_s2.0_S2352340919306675_main.pdf | original Data in Brief PDF mirror | Same article in PDF form |
| https://www.sciencedirect.com/science/article/pii/S0167739X18330760 | related research paper | Detection/identification task and open RF database context |
| https://al-sad.github.io/DroneRF/ | author project page | Dataset/code landing page and citation |
| https://github.com/Al-Sad/DroneRF | official code repository | LabVIEW/MATLAB/Python code repository |
| https://raw.githubusercontent.com/Al-Sad/DroneRF/master/Matlab/Main_1_Data_aggregation.m | official MATLAB code | Raw CSV L/H file loading and BUI mapping |
| https://raw.githubusercontent.com/Al-Sad/DroneRF/master/Matlab/Main_2_Data_labeling.m | official MATLAB code | Label generation levels |
| https://raw.githubusercontent.com/Al-Sad/DroneRF/master/Python/Classification.py | official Python code | Processed RF_Data.csv label rows |
