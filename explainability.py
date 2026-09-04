"""
Explainability (SHAP)
=======================
Generates global feature importance and individual patient-level
explanations for the XGBoost model (best PR-AUC / most clinically
deployed model type for this task).

This is the piece that makes the model usable in a hospital setting --
clinicians and care-management teams need to know WHY a patient was
flagged, not just that they were.
"""

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

MODEL_PATH = "/home/claude/readmission_project/outputs/models_and_splits.joblib"
OUT_DIR = "/home/claude/readmission_project/outputs"


def run_shap_analysis():
    bundle = joblib.load(MODEL_PATH)
    xgb_model = bundle["xgboost"]
    X_test = bundle["splits"]["X_test"]
    y_test = bundle["splits"]["y_test"]

    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer(X_test)

    # --- Global importance (summary beeswarm) ---
    plt.figure()
    shap.summary_plot(shap_values, X_test, show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/shap_global_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved global SHAP summary -> {OUT_DIR}/shap_global_summary.png")

    # --- Mean |SHAP| ranked feature importance table ---
    mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    importance_df = (
        pd.DataFrame({"feature": X_test.columns, "mean_abs_shap": mean_abs_shap})
        .sort_values("mean_abs_shap", ascending=False)
        .reset_index(drop=True)
    )
    importance_df.to_csv(f"{OUT_DIR}/shap_feature_importance.csv", index=False)
    print("\nTop 10 drivers of readmission risk:")
    print(importance_df.head(10).to_string(index=False))

    # --- Individual patient explanation: highest-risk patient in test set ---
    probs = xgb_model.predict_proba(X_test)[:, 1]
    highest_risk_idx = np.argmax(probs)

    plt.figure()
    shap.plots.waterfall(shap_values[highest_risk_idx], show=False, max_display=12)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/shap_individual_patient_example.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(
        f"\nSaved individual patient explanation (predicted risk = "
        f"{probs[highest_risk_idx]:.1%}) -> {OUT_DIR}/shap_individual_patient_example.png"
    )

    return importance_df


if __name__ == "__main__":
    run_shap_analysis()
