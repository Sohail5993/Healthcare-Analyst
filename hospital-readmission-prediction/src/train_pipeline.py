"""
Hospital 30-Day Readmission Prediction Pipeline
================================================
End-to-end script for a Healthcare Analyst portfolio project.

Steps:
1. Load Diabetes 130-US Hospitals dataset (OpenML)
2. Basic cleaning & feature engineering
3. Train/test split (stratified)
4. Train Logistic Regression, Random Forest, XGBoost
5. Evaluate (ROC-AUC, Precision-Recall, Classification Report)
6. SHAP explainability (global + local)
7. Save models, metrics, and figures
8. Estimate simple business impact (cost of readmissions)

Run from project root:
    python src/train_pipeline.py
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    XGBClassifier = None

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
FIGURES_DIR = ROOT / "reports" / "figures"
METRICS_DIR = ROOT / "reports" / "metrics"

for d in [MODELS_DIR, FIGURES_DIR, METRICS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.25

# Approximate US average cost of a 30-day readmission (illustrative)
AVG_READMISSION_COST_USD = 15_000


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load the Diabetes 130-Hospitals dataset (OpenML 43874)."""
    print("Loading Diabetes 130-US Hospitals dataset (OpenML)...")
    ds = fetch_openml(data_id=43874, as_frame=True, parser="auto")
    X = ds.data.copy()
    y = ds.target.astype(int)
    print(f"  Shape: {X.shape} | Positive rate: {y.mean():.1%}")
    return X, y


def basic_feature_engineering(X: pd.DataFrame) -> pd.DataFrame:
    """Lightweight cleaning + a few clinically sensible features.
    
    Critical: drop any columns that leak the target (readmitted / readmit_binary).
    """
    X = X.copy()

    # --- Leakage removal (OpenML 43874 still carries these) ---
    leak_cols = [c for c in X.columns if c.lower() in {
        "readmitted", "readmit_binary", "readmit_30_days", "readmission"
    }]
    if leak_cols:
        print(f"  Dropping leakage columns: {leak_cols}")
        X = X.drop(columns=leak_cols)

    # Age is often an ordered categorical string
    if "age" in X.columns and (X["age"].dtype == object or str(X["age"].dtype) == "str"):
        # Handle both "[70-80)" style and "'30 years or younger'" style
        def parse_age(val):
            s = str(val)
            if "younger" in s.lower():
                return 25
            if "older" in s.lower() or "90" in s:
                return 95
            import re
            m = re.search(r"(\d+)", s)
            return float(m.group(1)) if m else np.nan
        X["age_numeric"] = X["age"].map(parse_age)
        X = X.drop(columns=["age"])

    # Simple utilization intensity proxy
    if all(c in X.columns for c in ["num_lab_procedures", "num_procedures", "num_medications"]):
        X["utilization_score"] = (
            X["num_lab_procedures"].fillna(0).astype(float)
            + X["num_procedures"].fillna(0).astype(float) * 2
            + X["num_medications"].fillna(0).astype(float)
        )

    return X


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Numeric scaling + one-hot encoding for categoricals."""
    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ],
        remainder="drop",
    )
    return preprocessor


def train_and_evaluate(
    X_train, X_test, y_train, y_test, preprocessor
) -> dict:
    """Train three models and return metrics + fitted objects."""
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=20,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
            random_state=RANDOM_STATE,
            eval_metric="logloss",
            n_jobs=-1,
        )

    results = {}
    best_name, best_auc = None, -1.0

    for name, clf in models.items():
        print(f"\nTraining {name}...")
        pipe = Pipeline([("prep", preprocessor), ("clf", clf)])
        pipe.fit(X_train, y_train)

        y_proba = pipe.predict_proba(X_test)[:, 1]
        y_pred = (y_proba >= 0.5).astype(int)

        auc = roc_auc_score(y_test, y_proba)
        ap = average_precision_score(y_test, y_proba)

        print(f"  ROC-AUC: {auc:.4f} | Avg Precision: {ap:.4f}")
        print(classification_report(y_test, y_pred, target_names=["No Readmit", "Readmit 30d"]))

        results[name] = {
            "pipeline": pipe,
            "y_proba": y_proba,
            "y_pred": y_pred,
            "roc_auc": float(auc),
            "avg_precision": float(ap),
            "report": classification_report(y_test, y_pred, output_dict=True),
        }

        if auc > best_auc:
            best_auc = auc
            best_name = name

    print(f"\n>>> Best model by ROC-AUC: {best_name} ({best_auc:.4f})")
    return results, best_name


def plot_roc_pr(results: dict, y_test, out_dir: Path):
    """ROC and Precision-Recall curves for all models."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for name, res in results.items():
        fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
        axes[0].plot(fpr, tpr, lw=2, label=f"{name} (AUC={res['roc_auc']:.3f})")

        prec, rec, _ = precision_recall_curve(y_test, res["y_proba"])
        axes[1].plot(rec, prec, lw=2, label=f"{name} (AP={res['avg_precision']:.3f})")

    axes[0].plot([0, 1], [0, 1], "k--", lw=1)
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].set_title("ROC Curve")
    axes[0].legend(loc="lower right")

    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].set_title("Precision-Recall Curve")
    axes[1].legend(loc="upper right")

    plt.tight_layout()
    path = out_dir / "01_roc_pr_curves.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def plot_confusion(y_test, y_pred, name: str, out_dir: Path):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["No Readmit", "Readmit"],
        yticklabels=["No Readmit", "Readmit"],
    )
    plt.title(f"Confusion Matrix – {name}")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    path = out_dir / "02_confusion_matrix.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def run_shap(pipeline, X_test: pd.DataFrame, out_dir: Path, max_samples: int = 800):
    """Global SHAP summary for the best tree-based (or linear) model."""
    print("\nComputing SHAP values (this may take a minute)...")
    # Transform features
    X_trans = pipeline.named_steps["prep"].transform(X_test)
    feature_names = pipeline.named_steps["prep"].get_feature_names_out()

    clf = pipeline.named_steps["clf"]

    # Sample for speed
    if X_trans.shape[0] > max_samples:
        rng = np.random.RandomState(RANDOM_STATE)
        idx = rng.choice(X_trans.shape[0], max_samples, replace=False)
        X_shap = X_trans[idx]
    else:
        X_shap = X_trans
        idx = np.arange(X_trans.shape[0])

    # Prefer TreeExplainer when possible
    if hasattr(clf, "feature_importances_") or "XGB" in type(clf).__name__:
        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(X_shap)
        if isinstance(shap_values, list):  # RF sometimes returns list
            shap_values = shap_values[1]
    else:
        explainer = shap.LinearExplainer(clf, X_shap)
        shap_values = explainer.shap_values(X_shap)

    # Beeswarm
    plt.figure()
    shap.summary_plot(shap_values, X_shap, feature_names=feature_names, show=False, max_display=15)
    plt.title("SHAP Summary – Global Feature Impact on 30-Day Readmission")
    path = out_dir / "03_shap_beeswarm.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

    # Bar importance
    plt.figure()
    shap.summary_plot(shap_values, X_shap, feature_names=feature_names, plot_type="bar", show=False, max_display=15)
    plt.title("Mean |SHAP| Feature Importance")
    path = out_dir / "04_shap_bar.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

    return shap_values, feature_names, explainer


def estimate_impact(y_test, y_proba, threshold: float = 0.5) -> dict:
    """
    Simple illustrative business impact.
    Assumes we can intervene on high-risk patients and reduce their
    readmission rate by a conservative relative reduction (e.g. 15%).
    """
    n = len(y_test)
    actual_readmits = int(y_test.sum())
    predicted_high_risk = (y_proba >= threshold).sum()

    # Among true positives we assume a 15% relative reduction is achievable
    # with targeted discharge planning / follow-up (illustrative literature range)
    relative_reduction = 0.15
    tp = ((y_proba >= threshold) & (y_test == 1)).sum()
    preventable = int(tp * relative_reduction)
    savings = preventable * AVG_READMISSION_COST_USD

    return {
        "test_patients": n,
        "actual_30d_readmissions": actual_readmits,
        "flagged_high_risk": int(predicted_high_risk),
        "estimated_preventable_readmissions": preventable,
        "estimated_cost_savings_usd": savings,
        "assumptions": {
            "avg_cost_per_readmission_usd": AVG_READMISSION_COST_USD,
            "relative_reduction_among_intervened_true_positives": relative_reduction,
            "threshold": threshold,
        },
    }


def main():
    print("=" * 70)
    print("HOSPITAL 30-DAY READMISSION PREDICTION PIPELINE")
    print("=" * 70)

    # 1. Data
    X, y = load_data()
    X = basic_feature_engineering(X)

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTrain: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,}")

    # 3. Preprocessor
    preprocessor = build_preprocessor(X_train)

    # 4. Train & evaluate
    results, best_name = train_and_evaluate(X_train, X_test, y_train, y_test, preprocessor)
    best_pipe = results[best_name]["pipeline"]
    best_proba = results[best_name]["y_proba"]
    best_pred = results[best_name]["y_pred"]

    # 5. Plots
    plot_roc_pr(results, y_test, FIGURES_DIR)
    plot_confusion(y_test, best_pred, best_name, FIGURES_DIR)

    # 6. SHAP (prefer XGBoost or RF)
    shap_model_name = best_name
    if "XGBoost" in results:
        shap_model_name = "XGBoost"
    elif "Random Forest" in results:
        shap_model_name = "Random Forest"
    shap_pipe = results[shap_model_name]["pipeline"]
    if HAS_SHAP:
        run_shap(shap_pipe, X_test, FIGURES_DIR)
    else:
        print("SHAP not installed — skipping explainability plots.")

    # 7. Impact estimate
    impact = estimate_impact(y_test, best_proba)
    print("\n--- Illustrative Business Impact (Test Set) ---")
    print(f"  Actual 30-day readmissions : {impact['actual_30d_readmissions']:,}")
    print(f"  Flagged high-risk          : {impact['flagged_high_risk']:,}")
    print(f"  Est. preventable (15% RR)  : {impact['estimated_preventable_readmissions']:,}")
    print(f"  Est. cost savings          : ${impact['estimated_cost_savings_usd']:,.0f}")

    # 8. Persist
    joblib.dump(best_pipe, MODELS_DIR / "best_readmission_model.joblib")
    print(f"\nSaved model → {MODELS_DIR / 'best_readmission_model.joblib'}")

    metrics_out = {
        "best_model": best_name,
        "models": {
            name: {
                "roc_auc": res["roc_auc"],
                "avg_precision": res["avg_precision"],
            }
            for name, res in results.items()
        },
        "impact": impact,
    }
    with open(METRICS_DIR / "metrics.json", "w") as f:
        json.dump(metrics_out, f, indent=2)
    print(f"Saved metrics → {METRICS_DIR / 'metrics.json'}")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
