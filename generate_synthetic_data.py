"""
Synthetic Hospital Encounter Data Generator
=============================================
Generates a synthetic dataset that mirrors the structure of the real-world
UCI "Diabetes 130-US Hospitals" dataset (Strack et al., 2014) -- the most
widely used public benchmark for 30-day readmission modeling.

WHY SYNTHETIC DATA HERE:
This environment has no internet access to UCI/Kaggle. The schema, feature
distributions, and injected risk relationships below are built to closely
mirror the real dataset so this pipeline runs unmodified against it.

TO USE THE REAL DATASET INSTEAD:
1. Download from UCI: https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008
   or Kaggle: https://www.kaggle.com/datasets/brandao/diabetes
2. Save as data/raw_encounters.csv
3. Skip this script -- src/feature_engineering.py reads either source
   and will detect which one it's looking at automatically (see README).

Label definition (matches CMS 30-day readmission logic):
  readmitted_30d = 1 if patient returned as an inpatient within 30 days
                   of discharge, else 0.
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N_PATIENTS = 15000


def generate_encounters(n=N_PATIENTS) -> pd.DataFrame:
    df = pd.DataFrame({"patient_id": np.arange(1, n + 1)})

    # ---- Demographics ----
    df["age_group"] = RNG.choice(
        ["[0-30)", "[30-50)", "[50-60)", "[60-70)", "[70-80)", "[80-100)"],
        size=n, p=[0.03, 0.12, 0.17, 0.24, 0.26, 0.18],
    )
    df["gender"] = RNG.choice(["Female", "Male"], size=n, p=[0.53, 0.47])
    df["race"] = RNG.choice(
        ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"],
        size=n, p=[0.68, 0.19, 0.06, 0.03, 0.04],
    )

    # ---- Admission / encounter details ----
    df["admission_type"] = RNG.choice(
        ["Emergency", "Urgent", "Elective", "Newborn"], size=n, p=[0.55, 0.2, 0.23, 0.02]
    )
    df["admission_source"] = RNG.choice(
        ["Physician Referral", "Emergency Room", "Transfer", "Other"],
        size=n, p=[0.3, 0.45, 0.15, 0.10],
    )
    df["discharge_disposition"] = RNG.choice(
        ["Home", "Home Health Care", "Skilled Nursing Facility", "Other Facility"],
        size=n, p=[0.60, 0.15, 0.17, 0.08],
    )

    df["time_in_hospital"] = np.clip(RNG.poisson(4.2, size=n), 1, 14)
    df["num_lab_procedures"] = np.clip(RNG.normal(43, 20, size=n).astype(int), 1, 132)
    df["num_procedures"] = np.clip(RNG.poisson(1.3, size=n), 0, 6)
    df["num_medications"] = np.clip(RNG.normal(16, 8, size=n).astype(int), 1, 60)
    df["number_outpatient"] = np.clip(RNG.poisson(0.4, size=n), 0, 15)
    df["number_emergency"] = np.clip(RNG.poisson(0.25, size=n), 0, 10)
    df["number_inpatient_prior"] = np.clip(RNG.poisson(0.6, size=n), 0, 10)
    df["number_diagnoses"] = np.clip(RNG.normal(7.5, 2.5, size=n).astype(int), 1, 16)

    # ---- Clinical / comorbidity flags ----
    df["diag_diabetes"] = RNG.binomial(1, 0.55, size=n)
    df["diag_circulatory"] = RNG.binomial(1, 0.38, size=n)
    df["diag_respiratory"] = RNG.binomial(1, 0.20, size=n)
    df["diag_renal"] = RNG.binomial(1, 0.14, size=n)
    df["diag_cancer"] = RNG.binomial(1, 0.06, size=n)

    # ---- Labs / meds ----
    df["A1Cresult"] = RNG.choice(["None", "Norm", ">7", ">8"], size=n, p=[0.5, 0.08, 0.1, 0.32])
    df["max_glu_serum"] = RNG.choice(["None", "Norm", ">200", ">300"], size=n, p=[0.85, 0.03, 0.06, 0.06])
    df["insulin"] = RNG.choice(["No", "Steady", "Up", "Down"], size=n, p=[0.45, 0.3, 0.13, 0.12])
    df["med_change"] = RNG.choice(["No", "Ch"], size=n, p=[0.55, 0.45])
    df["diabetesMed"] = RNG.choice(["No", "Yes"], size=n, p=[0.23, 0.77])

    # ---- Utilization history ----
    df["num_prior_admissions_1yr"] = np.clip(RNG.poisson(0.8, size=n), 0, 12)

    return df


def inject_readmission_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a latent risk score from clinically plausible drivers, then sample
    the binary 30-day readmission label from it (adds realistic noise so no
    model can achieve trivial/perfect separation).
    """
    age_risk = df["age_group"].map({
        "[0-30)": -0.6, "[30-50)": -0.2, "[50-60)": 0.0,
        "[60-70)": 0.2, "[70-80)": 0.4, "[80-100)": 0.6,
    }).astype(float)

    disp_risk = df["discharge_disposition"].map({
        "Home": -0.3, "Home Health Care": 0.2,
        "Skilled Nursing Facility": 0.5, "Other Facility": 0.3,
    }).astype(float)

    admit_risk = df["admission_type"].map({
        "Emergency": 0.3, "Urgent": 0.15, "Elective": -0.2, "Newborn": -0.5
    }).astype(float)

    a1c_risk = df["A1Cresult"].map({"None": 0.0, "Norm": -0.1, ">7": 0.15, ">8": 0.3}).astype(float)

    logit = (
        -2.9
        + age_risk
        + disp_risk
        + admit_risk
        + a1c_risk
        + 0.35 * df["number_inpatient_prior"].clip(upper=5)
        + 0.30 * df["number_emergency"].clip(upper=5)
        + 0.18 * df["number_outpatient"].clip(upper=5)
        + 0.22 * df["num_prior_admissions_1yr"].clip(upper=5)
        + 0.05 * (df["time_in_hospital"] - 4)
        + 0.02 * (df["num_medications"] - 16)
        + 0.25 * df["diag_renal"]
        + 0.20 * df["diag_circulatory"]
        + 0.15 * df["diag_respiratory"]
        + 0.15 * (df["diabetesMed"] == "Yes").astype(int)
        + 0.10 * (df["med_change"] == "Ch").astype(int)
        + RNG.normal(0, 0.55, size=len(df))  # unobserved variation / noise
    )

    prob = 1 / (1 + np.exp(-logit))
    df["readmitted_30d"] = RNG.binomial(1, prob)
    return df


def main():
    df = generate_encounters()
    df = inject_readmission_label(df)
    out_path = "/home/claude/readmission_project/data/encounters.csv"
    df.to_csv(out_path, index=False)
    rate = df["readmitted_30d"].mean()
    print(f"Generated {len(df):,} encounters -> {out_path}")
    print(f"30-day readmission rate: {rate:.1%}  (real-world hospitals: ~11-20%)")


if __name__ == "__main__":
    main()
