"""
Cost / Impact Analysis
========================
Translates model performance into an operational and financial business
case: if a hospital used this model to target a limited-capacity care
management (transitional care) program at the highest-risk patients,
what's the expected reduction in readmissions and dollar impact?

Assumptions are made explicit and are based on published ranges:
  - Avg cost of a 30-day readmission: ~$15,200 (HCUP / AHRQ estimates,
    medical-surgical admissions)
  - Transitional care programs (e.g. nurse follow-up calls, med
    reconciliation, post-discharge clinic visits) reduce readmission
    risk by ~20-30% for enrolled high-risk patients (per RCT literature,
    e.g. Coleman Care Transitions Intervention, Project RED)
  - Program cost: ~$400-600 per enrolled patient
  - CMS HRRP penalty: up to 3% of total Medicare inpatient payments for
    excess readmissions -- modeled here as a simple avoided-penalty proxy

These are configurable -- swap in a hospital's actual finance data for
a real deployment.
"""

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = "/home/claude/readmission_project/outputs/models_and_splits.joblib"
OUT_DIR = "/home/claude/readmission_project/outputs"

# ---- Configurable assumptions ----
COST_PER_READMISSION = 15_200        # $, avg cost of an unplanned readmission
PROGRAM_COST_PER_PATIENT = 500        # $, cost to enroll one patient in transitional care
RELATIVE_RISK_REDUCTION = 0.25        # 25% reduction in readmission risk for enrolled patients
INTERVENTION_CAPACITY_FRACTIONS = [0.05, 0.10, 0.15, 0.20, 0.30]  # % of discharges targetable


def simulate_impact():
    bundle = joblib.load(MODEL_PATH)
    xgb_model = bundle["xgboost"]
    X_test = bundle["splits"]["X_test"]
    y_test = bundle["splits"]["y_test"].reset_index(drop=True)

    risk_scores = xgb_model.predict_proba(X_test)[:, 1]
    n_patients = len(y_test)
    baseline_readmissions = y_test.sum()
    baseline_rate = y_test.mean()

    order = np.argsort(-risk_scores)
    rows = []

    for frac in INTERVENTION_CAPACITY_FRACTIONS:
        k = int(np.ceil(n_patients * frac))
        targeted_idx = order[:k]
        targeted_actual_readmits = y_test.iloc[targeted_idx].sum()

        # Readmissions prevented among the targeted, truly-high-risk group
        readmissions_prevented = targeted_actual_readmits * RELATIVE_RISK_REDUCTION

        gross_savings = readmissions_prevented * COST_PER_READMISSION
        program_cost = k * PROGRAM_COST_PER_PATIENT
        net_savings = gross_savings - program_cost
        roi = (net_savings / program_cost) if program_cost > 0 else np.nan

        new_readmissions = baseline_readmissions - readmissions_prevented
        new_rate = new_readmissions / n_patients
        rate_reduction_pct = (baseline_rate - new_rate) / baseline_rate

        rows.append({
            "capacity_targeted_pct": f"{frac:.0%}",
            "patients_enrolled": k,
            "readmissions_in_targeted_group": int(targeted_actual_readmits),
            "est_readmissions_prevented": round(readmissions_prevented, 1),
            "program_cost_$": program_cost,
            "gross_savings_$": round(gross_savings),
            "net_savings_$": round(net_savings),
            "roi": round(roi, 2),
            "readmission_rate_reduction": f"{rate_reduction_pct:.1%}",
        })

    impact_df = pd.DataFrame(rows)
    impact_df.to_csv(f"{OUT_DIR}/cost_impact_analysis.csv", index=False)

    print(f"Test cohort: {n_patients:,} patients | baseline readmission rate: {baseline_rate:.1%}")
    print(f"Assumptions: ${COST_PER_READMISSION:,}/readmission | "
          f"${PROGRAM_COST_PER_PATIENT}/enrolled patient | "
          f"{RELATIVE_RISK_REDUCTION:.0%} relative risk reduction\n")
    print(impact_df.to_string(index=False))

    # Annualized extrapolation for a mid-size hospital (illustrative)
    annual_discharges = 20_000
    best_row = impact_df.iloc[(impact_df["roi"]).idxmax()]
    scale_factor = annual_discharges / n_patients
    print(f"\n--- Annualized estimate for a {annual_discharges:,}-discharge/year hospital ---")
    print(f"Using {best_row['capacity_targeted_pct']} capacity tier (best ROI): "
          f"${best_row['net_savings_$'] * scale_factor:,.0f} net savings/year, "
          f"{float(best_row['readmission_rate_reduction'].strip('%')):.1f}% relative readmission-rate reduction")

    return impact_df


if __name__ == "__main__":
    simulate_impact()
