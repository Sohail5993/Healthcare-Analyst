# Data

This project uses the **Diabetes 130-US Hospitals (1999–2008)** dataset, a widely used public clinical dataset for 30-day hospital readmission prediction research.

## Source
- Original paper: Strack et al., *Impact of HbA1c Measurement on Hospital Readmission Rates*, Biomed Res Int, 2014
- UCI / OpenML version (binarized 30-day target): OpenML data_id = **43874**
- Also available via Fairlearn: `fairlearn.datasets.fetch_diabetes_hospital`

## How the data is loaded
The main pipeline (`src/train_pipeline.py`) automatically downloads the dataset via `sklearn.datasets.fetch_openml` the first time it runs. No manual download is required.

## Target
- `readmit_30_days`: 1 = readmitted within 30 days, 0 = otherwise
- Class imbalance: ~11% positive (typical for real 30-day readmission rates)

## Notes
- This is **de-identified real clinical data** from 130 US hospitals (1999–2008).
- Suitable for portfolio / research use under the original dataset terms.
- Always treat healthcare data with care even when de-identified.
