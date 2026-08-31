# Hospital 30-Day Readmission Prediction

Predicts which patients are at high risk of unplanned readmission within
30 days of discharge, so a hospital's care-management team can target a
limited-capacity intervention program at the patients who need it most.

## Why this matters

Under CMS's Hospital Readmissions Reduction Program (HRRP), hospitals with
excess 30-day readmissions face payment penalties of up to 3% of total
Medicare inpatient reimbursement. Beyond the penalty, each avoidable
readmission costs roughly **$15,000** and represents a real gap in care
quality. A model that reliably flags high-risk patients at discharge lets
hospitals target transitional-care resources (follow-up calls, med
reconciliation, early post-discharge visits) where they'll have the most
impact.

## Project structure

```
readmission_project/
├── data/
│   └── generate_synthetic_data.py   # synthetic EHR data (schema mirrors UCI Diabetes 130-Hospitals)
├── src/
│   ├── feature_engineering.py       # encoding, composite risk features
│   ├── train_models.py              # LogReg / Random Forest / XGBoost
│   ├── evaluate.py                  # AUC, PR-AUC, calibration, precision@K
│   ├── explainability.py            # SHAP global + individual patient
│   └── cost_impact.py               # $ savings / ROI / CMS penalty framing
├── outputs/                          # all generated metrics, plots, CSVs
├── main.py                           # runs the full pipeline end-to-end
└── README.md
```

## Quickstart

```bash
pip install pandas numpy scikit-learn xgboost shap matplotlib
python main.py
```

This runs the full pipeline and writes everything to `outputs/`:
- `model_comparison_metrics.csv` — AUC, PR-AUC, precision/recall per model
- `evaluation_curves.png` — ROC, PR, and calibration curves
- `shap_global_summary.png` — top risk drivers across the population
- `shap_feature_importance.csv` — ranked feature importance table
- `shap_individual_patient_example.png` — one patient's risk explained
- `cost_impact_analysis.csv` — savings/ROI at different intervention capacities

## Using real data instead of the synthetic set

This environment can't reach UCI/Kaggle directly, so `data/generate_synthetic_data.py`
builds a synthetic dataset with the **same schema and realistic feature
relationships** as the standard public benchmark for this problem — the UCI
**"Diabetes 130-US Hospitals for Years 1999–2008"** dataset (Strack et al.,
2014; ~101,766 real encounters, the dataset most portfolio/production
readmission models are built and validated on).

To swap in the real thing:
1. Download from [UCI](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008)
   or [Kaggle](https://www.kaggle.com/datasets/brandao/diabetes)
2. Rename columns to match `data/generate_synthetic_data.py`'s output schema
   (or adjust `src/feature_engineering.py`'s column lists to match the raw
   file's actual column names)
3. Save as `data/encounters.csv` and re-run `main.py`

Other good real sources for this problem if you want to extend it:
- **CMS Medicare claims (SynPUF / research files)** — richer utilization & cost history
- **Synthea** — fully synthetic but longitudinally realistic EHR generator,
  useful for simulating a specific patient population (e.g., CHF, COPD cohorts)
- **MIMIC-IV** (requires credentialed access) — real ICU/hospital data, gold
  standard for clinical ML research

## Modeling approach

**Three models, escalating complexity:**
| Model | Role |
|---|---|
| Logistic Regression | Interpretable baseline; coefficients directly reviewable by clinical stakeholders |
| Random Forest | Captures non-linear interactions without heavy tuning |
| XGBoost | Best PR-AUC in most published readmission studies; used for SHAP explainability |

**Class imbalance** (~19% positive rate here, consistent with real hospital
readmission rates) is handled via `class_weight="balanced"` / `scale_pos_weight`
rather than oversampling, to keep predicted probabilities honest for
risk-stratification rather than distorting them via synthetic resampling.

**Why PR-AUC over ROC-AUC as the primary metric:** with an imbalanced
outcome, ROC-AUC can look deceptively good while precision at any
operationally realistic threshold stays low. PR-AUC and precision@top-K%
are what actually tell you "if we can only intervene on the top 10-20% of
discharges, how many of the true positives do we catch."

**Realistic performance expectations:** published 30-day readmission models
(including CMS's own) typically achieve ROC-AUC in the **0.65–0.70** range.
This isn't a modeling limitation — readmission is driven heavily by factors
outside the EHR (social determinants, housing, caregiver support, post-discharge
adherence), so this ceiling is expected and worth calling out explicitly
rather than over-claiming performance.

## Explainability

SHAP (TreeExplainer on XGBoost) provides:
- **Global summary** — which features drive risk across the population
  (typically: prior utilization, discharge disposition, age, admission
  type — all clinically sensible and literature-consistent)
- **Individual explanations** — a waterfall plot for any single patient,
  so a care coordinator can see *why* a specific patient was flagged,
  not just their risk score. This is the difference between a model that
  gets used and one that gets ignored by clinical staff.

## Cost / impact framing

`cost_impact.py` converts model performance into a business case:
- Sweeps intervention capacity (5%–30% of discharges, matching realistic
  care-management team sizes)
- Applies a literature-based ~25% relative risk reduction for enrolled
  high-risk patients (consistent with Coleman Care Transitions
  Intervention / Project RED RCT results)
- Reports net savings and ROI per capacity tier, plus an annualized
  estimate for a representative hospital

All dollar assumptions are parameterized at the top of `cost_impact.py` —
swap in your hospital's actual per-readmission cost and program cost for
a real business case.

## Evaluation metrics reported

- ROC-AUC, PR-AUC (average precision)
- Precision @ top-10% / top-20% risk
- Precision / Recall / F1 at an operational threshold (top 20% flagged)
- Calibration curve (are predicted probabilities trustworthy?)

## Next steps for a production version

1. Validate on real claims/EHR data with a proper temporal holdout (train
   on earlier years, test on later ones — this dataset uses a random split)
2. Add social determinants of health (SDOH) features if available —
   consistently the biggest gap between EHR-only models and true ceiling performance
2. Fairness audit: check calibration and error rates across race/age/gender
   subgroups before deployment
3. Threshold selection in partnership with the care-management team based
   on actual program capacity, not just F1
4. Monitor for model/data drift — readmission drivers shift with policy,
   staffing, and population changes
