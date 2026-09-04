# 🏥 Hospital 30-Day Readmission Prediction

**End-to-end Healthcare Analytics project** that predicts patients at high risk of unplanned 30-day hospital readmission and explains *why* using SHAP.

> **Why this matters**  
> Unplanned 30-day readmissions are a key quality metric. CMS and other payers penalize hospitals for excess rates. Identifying high-risk patients early enables targeted discharge planning, follow-up calls, and care coordination — reducing cost and improving outcomes.

---

## 📌 Project Highlights

| Area | Details |
|------|---------|
| **Problem** | Binary classification – will the patient be readmitted within 30 days? |
| **Dataset** | Diabetes 130-US Hospitals (1999–2008) – ~101,766 encounters from 130 hospitals |
| **Models** | Logistic Regression · Random Forest · **XGBoost** |
| **Explainability** | SHAP (global beeswarm + bar importance + patient-level ready) |
| **Impact lens** | Estimated preventable readmissions & illustrative cost savings |
| **Stack** | Python · pandas · scikit-learn · XGBoost · SHAP · matplotlib/seaborn |

---

## 🗂️ Repository Structure

```
hospital-readmission-prediction/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py                      # Streamlit interactive demo
├── data/
│   └── README.md               # Dataset source & notes
├── src/
│   ├── train_pipeline.py       # Full reproducible pipeline
│   └── shap_interactions.py   # SHAP interaction values & plots
├── models/                     # Saved best model (.joblib)
├── reports/
│   ├── figures/                # ROC, PR, confusion matrix, SHAP plots
│   └── metrics/                # metrics.json
└── notebooks/                  # (optional) exploratory notebooks
```

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/<your-username>/hospital-readmission-prediction.git
cd hospital-readmission-prediction

# 2. Environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Run the full pipeline (downloads data automatically)
python src/train_pipeline.py

# 4. Launch the interactive Streamlit demo
streamlit run app.py
```

The training script will:
1. Download the OpenML dataset (first run only)
2. Clean + engineer features
3. Train three models
4. Evaluate with ROC-AUC, Average Precision, classification reports
5. Generate SHAP explanations
6. Save model, metrics, and figures under `models/` and `reports/`

**Streamlit demo (`app.py`)** loads the saved model and lets you:
- Switch between lower-risk / higher-risk preset profiles
- Adjust demographics, utilization, clinical indicators, and prior-visit flags
- See live 30-day readmission probability and risk tier (Low / Medium / High)
- **Driver list**: SHAP local explanation when `shap` is installed; otherwise a sensitivity-based driver table (always available)

---

## 📊 Results (from latest pipeline run)

Stratified 75/25 hold-out on ~101k encounters (~11% 30-day readmission rate):

| Model                  | ROC-AUC | Avg Precision |
|------------------------|---------|---------------|
| Logistic Regression    | 0.638   | 0.167         |
| **Random Forest** (best)| **0.649** | **0.181**   |
| XGBoost                | 0.645   | 0.179         |

> The positive class is rare (~11%). Accuracy is a poor metric here — ROC-AUC and Average Precision are the right lenses.  
> These numbers are realistic for this classic dataset with light feature engineering; stronger results usually require richer longitudinal features or external data.

**SHAP** highlights clinically sensible drivers (utilization intensity, number of diagnoses, discharge disposition, time in hospital, diabetes-related indicators, etc.).

### Illustrative Business Impact (test set)
- Actual 30-day readmissions: **2,839**
- Flagged high-risk (threshold 0.5): **9,533**
- Estimated preventable readmissions (15% relative reduction on true positives): **~242**
- Estimated cost savings (at $15k / readmission): **~$3.6 M** on the test cohort alone

Assumptions are deliberately conservative and fully documented in `reports/metrics/metrics.json`.

---

## 💰 Business Impact Framing

The pipeline includes a simple, transparent impact estimator:

- Average cost of a 30-day readmission ≈ **$15,000** (US literature ballpark)
- Assume a conservative **15% relative reduction** among true-positive patients who receive enhanced discharge support
- On the test set this produces an **illustrative annualized savings figure** you can scale to a real hospital volume

This is intentionally conservative and fully documented in `reports/metrics/metrics.json` so reviewers can change the assumptions.

---

## 🔍 Skills Demonstrated

- Healthcare domain framing (CMS readmission penalties, quality metrics)
- Working with real clinical tabular data (missingness, categorical encodings, class imbalance)
- Feature engineering for utilization & clinical intensity
- Model comparison (linear vs tree ensembles)
- Proper evaluation under imbalance (ROC-AUC + Precision-Recall)
- **SHAP** for global and (extendable) local explainability
- Reproducible pipeline + artifact management
- Communicating results in business terms (cost, preventable events)

---

## 🛠️ Tech Stack

- **Python 3.10+**
- pandas, NumPy
- scikit-learn (preprocessing, LogisticRegression, RandomForest, metrics)
- XGBoost
- SHAP
- matplotlib / seaborn
- joblib
- (Optional) Streamlit for interactive demo

---

## 📚 Data Citation

Strack B, DeShazo JP, Gennings C, et al.  
*Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records.*  
BioMed Research International, 2014.  
OpenML / Fairlearn preprocessed version (data_id 43874).

---

## 🧭 Next Steps You Can Add

- [ ] Threshold tuning / cost-sensitive optimization
- [ ] Fairness analysis (race, gender, age groups)
- [x] Local driver list in Streamlit (SHAP when available + sensitivity fallback)
- [x] Simple Streamlit risk calculator (`app.py`)
- [ ] SQL feature store layer or dbt models
- [ ] Monitoring / drift detection sketch

---

## 👤 Author

**Aimms Consuting**  
Strategic Foresighted Semantic BI Analyst  
“Let’s Color The Daring Dreams Together”

---

*This project is for educational and portfolio purposes. It is not a clinical decision-support system and must not be used for real patient care without rigorous validation, regulatory review, and clinical governance.*
