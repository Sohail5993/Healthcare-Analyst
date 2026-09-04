"""
Feature Engineering
====================
Transforms raw encounter-level data into a model-ready matrix.

Design notes:
- Ordinal encode age_group (it has a natural order -> preserves signal
  a one-hot would throw away).
- One-hot encode nominal categoricals (race, admission_type, etc.).
- Engineer a few clinically-motivated composite features that are known
  strong predictors in the readmission literature (utilization history,
  comorbidity burden, care-transition risk).
"""

import numpy as np
import pandas as pd

AGE_ORDER = {
    "[0-30)": 0, "[30-50)": 1, "[50-60)": 2,
    "[60-70)": 3, "[70-80)": 4, "[80-100)": 5,
}

CATEGORICAL_COLS = [
    "gender", "race", "admission_type", "admission_source",
    "discharge_disposition", "A1Cresult", "max_glu_serum",
    "insulin", "med_change", "diabetesMed",
]

COMORBID_COLS = ["diag_diabetes", "diag_circulatory", "diag_respiratory", "diag_renal", "diag_cancer"]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Ordinal age
    df["age_ordinal"] = df["age_group"].map(AGE_ORDER)

    # Composite: total comorbidity burden
    df["comorbidity_count"] = df[COMORBID_COLS].sum(axis=1)

    # Composite: prior utilization (strongest known readmission predictor)
    df["total_prior_utilization"] = (
        df["number_outpatient"] + df["number_emergency"] + df["number_inpatient_prior"]
    )

    # Care-transition risk flag: discharged somewhere other than home
    df["high_risk_discharge"] = (df["discharge_disposition"] != "Home").astype(int)

    # Polypharmacy flag (>= 15 meds is a common clinical threshold)
    df["polypharmacy"] = (df["num_medications"] >= 15).astype(int)

    # Long stay flag
    df["extended_stay"] = (df["time_in_hospital"] >= 7).astype(int)

    # One-hot encode nominal categoricals
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)

    # Drop identifiers / original age_group / label stays separate
    df = df.drop(columns=["age_group"], errors="ignore")

    return df


def build_feature_matrix(df: pd.DataFrame, label_col: str = "readmitted_30d"):
    df_feat = engineer_features(df)
    y = df_feat[label_col]
    X = df_feat.drop(columns=[label_col, "patient_id"], errors="ignore")
    # Ensure all-numeric, boolean -> int
    X = X.astype({c: "int" for c in X.select_dtypes(bool).columns})
    return X, y


if __name__ == "__main__":
    raw = pd.read_csv("/home/claude/readmission_project/data/encounters.csv")
    X, y = build_feature_matrix(raw)
    print(f"Feature matrix: {X.shape[0]:,} rows x {X.shape[1]} features")
    print(f"Positive class rate: {y.mean():.1%}")
    print("\nSample features:", list(X.columns[:15]))
