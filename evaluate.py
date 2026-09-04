"""
Model Evaluation
=================
Compares Logistic Regression, Random Forest, and XGBoost on held-out test
data using metrics appropriate for imbalanced clinical classification:

- ROC-AUC          : overall discrimination (threshold-independent)
- PR-AUC            : more informative than ROC-AUC under class imbalance --
                      what actually matters for "can we find the high-risk
                      minority efficiently"
- Calibration       : are predicted probabilities trustworthy for
                      risk-stratification / clinical decision support?
- Precision@K       : precision if care-management team can only intervene
                      on the top-K% highest-risk patients (realistic
                      operational constraint)
"""

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score, precision_recall_curve, roc_auc_score, roc_curve,
    confusion_matrix, precision_score, recall_score, f1_score,
)

MODEL_PATH = "/home/claude/readmission_project/outputs/models_and_splits.joblib"
OUT_DIR = "/home/claude/readmission_project/outputs"


def get_probas(model_name, models, scaler, X_test):
    model = models[model_name]
    if model_name == "logistic_regression":
        return model.predict_proba(scaler.transform(X_test))[:, 1]
    return model.predict_proba(X_test)[:, 1]


def precision_at_k(y_true, y_score, k_frac):
    n = len(y_true)
    k = int(np.ceil(n * k_frac))
    order = np.argsort(-y_score)
    top_k_idx = order[:k]
    return y_true.iloc[top_k_idx].mean() if hasattr(y_true, "iloc") else y_true[top_k_idx].mean()


def evaluate_all():
    bundle = joblib.load(MODEL_PATH)
    models = {k: bundle[k] for k in ["logistic_regression", "random_forest", "xgboost"]}
    scaler = bundle["scaler"]
    X_test, y_test = bundle["splits"]["X_test"], bundle["splits"]["y_test"]

    results = []
    roc_data, pr_data, calib_data = {}, {}, {}

    for name in models:
        y_score = get_probas(name, models, scaler, X_test)

        roc_auc = roc_auc_score(y_test, y_score)
        pr_auc = average_precision_score(y_test, y_score)
        p_at_10 = precision_at_k(y_test, y_score, 0.10)
        p_at_20 = precision_at_k(y_test, y_score, 0.20)

        # Fixed operating threshold: flag top 20% risk (typical care-mgmt capacity)
        threshold = np.percentile(y_score, 80)
        y_pred = (y_score >= threshold).astype(int)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        results.append({
            "model": name, "roc_auc": roc_auc, "pr_auc": pr_auc,
            "precision_at_top10pct": p_at_10, "precision_at_top20pct": p_at_20,
            "precision_at_thresh": prec, "recall_at_thresh": rec, "f1_at_thresh": f1,
        })

        roc_data[name] = roc_curve(y_test, y_score)
        pr_data[name] = precision_recall_curve(y_test, y_score)
        calib_data[name] = calibration_curve(y_test, y_score, n_bins=10)

    results_df = pd.DataFrame(results).sort_values("pr_auc", ascending=False)
    results_df.to_csv(f"{OUT_DIR}/model_comparison_metrics.csv", index=False)
    print(results_df.to_string(index=False))

    plot_curves(roc_data, pr_data, calib_data, y_test)
    return results_df, models, scaler, X_test, y_test


def plot_curves(roc_data, pr_data, calib_data, y_test):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    base_rate = y_test.mean()

    for name, (fpr, tpr, _) in roc_data.items():
        axes[0].plot(fpr, tpr, label=name)
    axes[0].plot([0, 1], [0, 1], "k--", alpha=0.3)
    axes[0].set_xlabel("False Positive Rate"); axes[0].set_ylabel("True Positive Rate")
    axes[0].set_title("ROC Curve"); axes[0].legend()

    for name, (prec, rec, _) in pr_data.items():
        axes[1].plot(rec, prec, label=name)
    axes[1].axhline(base_rate, color="k", linestyle="--", alpha=0.3, label="baseline rate")
    axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision")
    axes[1].set_title("Precision-Recall Curve"); axes[1].legend()

    for name, (frac_pos, mean_pred) in calib_data.items():
        axes[2].plot(mean_pred, frac_pos, marker="o", label=name)
    axes[2].plot([0, 1], [0, 1], "k--", alpha=0.3)
    axes[2].set_xlabel("Mean Predicted Probability"); axes[2].set_ylabel("Fraction of Positives")
    axes[2].set_title("Calibration Curve"); axes[2].legend()

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/evaluation_curves.png", dpi=150)
    print(f"\nSaved evaluation plots -> {OUT_DIR}/evaluation_curves.png")


if __name__ == "__main__":
    evaluate_all()
