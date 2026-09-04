"""
SHAP Interaction Analysis — Hospital 30-Day Readmission
=======================================================
Produces practical interaction views:

  1. Main SHAP values (TreeExplainer)
  2. Dependence plots colored by interacting features
  3. Approximate strongest interactors per top feature
  4. Small-sample true interaction heatmap + pair ranking

Run from project root:
    python src/shap_interactions.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-whitegrid")

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "best_readmission_model.joblib"
FIG_DIR = ROOT / "reports" / "figures"
METRICS_DIR = ROOT / "reports" / "metrics"
FIG_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
MAX_SAMPLES = 500
HEATMAP_SAMPLES = 80
TOP_K = 8


def load_xy():
    ds = fetch_openml(data_id=43874, as_frame=True, parser="auto")
    X = ds.data.copy()
    y = ds.target.astype(int)

    leak = [
        c
        for c in X.columns
        if c.lower() in {"readmitted", "readmit_binary", "readmit_30_days", "readmission"}
    ]
    X = X.drop(columns=leak)

    def parse_age(val):
        s = str(val).lower()
        if "younger" in s:
            return 25.0
        if "over 60" in s or "older" in s:
            return 70.0
        import re
        m = re.search(r"(\d+)", s)
        return float(m.group(1)) if m else 55.0

    if "age" in X.columns:
        X["age_numeric"] = X["age"].map(parse_age)
        X = X.drop(columns=["age"])

    if all(c in X.columns for c in ["num_lab_procedures", "num_procedures", "num_medications"]):
        X["utilization_score"] = (
            X["num_lab_procedures"].fillna(0).astype(float)
            + X["num_procedures"].fillna(0).astype(float) * 2
            + X["num_medications"].fillna(0).astype(float)
        )

    for c in ["medicare", "medicaid", "had_emergency", "had_inpatient_days", "had_outpatient_days"]:
        if c in X.columns:
            X[c] = X[c].astype(str)

    return X, y


def main():
    print("=" * 70)
    print("SHAP INTERACTION ANALYSIS — 30-Day Readmission")
    print("=" * 70)

    if not MODEL_PATH.exists():
        raise SystemExit(f"Model not found: {MODEL_PATH}\nRun python src/train_pipeline.py first.")

    pipe = joblib.load(MODEL_PATH)
    prep = pipe.named_steps["prep"]
    clf = pipe.named_steps["clf"]

    X, y = load_xy()
    _, X_test, _, _ = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    rng = np.random.RandomState(RANDOM_STATE)
    n = min(MAX_SAMPLES, len(X_test))
    idx = rng.choice(len(X_test), n, replace=False)
    X_sample = X_test.iloc[idx].reset_index(drop=True)

    print(f"\n[1/5] Transforming {n} samples...")
    X_trans = prep.transform(X_sample)
    feature_names = list(prep.get_feature_names_out())
    short_names = [
        fn.replace("num__", "").replace("cat__", "").replace("_", " ") for fn in feature_names
    ]
    X_trans_df = pd.DataFrame(X_trans, columns=short_names)

    print("[2/5] Computing main SHAP values (TreeExplainer)...")
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X_trans)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    shap_values = np.array(shap_values)
    print(f"  SHAP matrix shape: {shap_values.shape}")

    mean_abs = np.abs(shap_values).mean(axis=0)
    top_idx = np.argsort(mean_abs)[::-1][:TOP_K]
    print("\nTop features by mean |SHAP|:")
    for rank, i in enumerate(top_idx, 1):
        print(f"  {rank:2d}. {short_names[i]:<42} {mean_abs[i]:.4f}")

    print("\n[3/5] Dependence plots with interaction coloring...")
    primary = int(top_idx[0])

    plt.figure(figsize=(9, 6))
    shap.dependence_plot(
        primary, shap_values, X_trans_df, interaction_index="auto", show=False
    )
    plt.title(f"Dependence: {short_names[primary]} (color = strongest interactor)")
    plt.tight_layout()
    p1 = FIG_DIR / "05_shap_dependence_interaction.png"
    plt.savefig(p1, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {p1.name}")

    if len(top_idx) >= 2:
        secondary = int(top_idx[1])
        plt.figure(figsize=(9, 6))
        shap.dependence_plot(
            primary, shap_values, X_trans_df, interaction_index=secondary, show=False
        )
        plt.title(
            f"Dependence: {short_names[primary]} colored by {short_names[secondary]}"
        )
        plt.tight_layout()
        p2 = FIG_DIR / "06_shap_dependence_pair.png"
        plt.savefig(p2, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved {p2.name}")

    if len(top_idx) >= 3:
        plt.figure(figsize=(9, 6))
        shap.dependence_plot(
            int(top_idx[1]),
            shap_values,
            X_trans_df,
            interaction_index=int(top_idx[2]),
            show=False,
        )
        plt.title(
            f"Dependence: {short_names[top_idx[1]]} colored by {short_names[top_idx[2]]}"
        )
        plt.tight_layout()
        p2b = FIG_DIR / "06b_shap_dependence_pair2.png"
        plt.savefig(p2b, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved {p2b.name}")

    print("\n[4/5] Approximate strongest interactors per top feature...")
    rows = []
    for i in top_idx:
        try:
            inter_ranks = shap.utils.approximate_interactions(int(i), shap_values, X_trans)
            for rank, j in enumerate(inter_ranks[:5]):
                if j == i:
                    continue
                rows.append(
                    {
                        "feature": short_names[i],
                        "interacts_with": short_names[j],
                        "approx_rank": rank + 1,
                    }
                )
        except Exception as e:
            print(f"  approximate_interactions failed for {short_names[i]}: {e}")

    approx_df = pd.DataFrame(rows)
    if len(approx_df):
        out_approx = METRICS_DIR / "shap_approximate_interactions.csv"
        approx_df.to_csv(out_approx, index=False)
        print(approx_df.head(15).to_string(index=False))
        print(f"  Saved {out_approx.name}")

    print(f"\n[5/5] True interaction matrix on {HEATMAP_SAMPLES} samples...")
    try:
        idx_h = rng.choice(len(X_test), min(HEATMAP_SAMPLES, len(X_test)), replace=False)
        X_h_trans = prep.transform(X_test.iloc[idx_h])

        iv = explainer.shap_interaction_values(X_h_trans)
        if isinstance(iv, list):
            iv = iv[1]
        iv = np.array(iv)

        k = len(top_idx)
        heat = np.zeros((k, k))
        for a, i in enumerate(top_idx):
            for b, j in enumerate(top_idx):
                heat[a, b] = np.abs(iv[:, i, j]).mean()

        top_names = [short_names[i] for i in top_idx]
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            heat,
            xticklabels=top_names,
            yticklabels=top_names,
            cmap="magma",
            annot=True,
            fmt=".3f",
            square=True,
            cbar_kws={"label": "Mean |phi_ij|"},
        )
        plt.title("SHAP Interaction Strength Heatmap (Top Features)")
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        plt.tight_layout()
        p3 = FIG_DIR / "07_shap_interaction_heatmap.png"
        plt.savefig(p3, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved {p3.name}")

        pairs = []
        for a, i in enumerate(top_idx):
            for b, j in enumerate(top_idx):
                if i >= j:
                    continue
                pairs.append(
                    {
                        "feature_a": short_names[i],
                        "feature_b": short_names[j],
                        "mean_abs_interaction": float(np.abs(iv[:, i, j]).mean()),
                        "mean_signed_interaction": float(iv[:, i, j].mean()),
                    }
                )
        pairs_df = pd.DataFrame(pairs).sort_values(
            "mean_abs_interaction", ascending=False
        )
        out_pairs = METRICS_DIR / "shap_interactions_top_pairs.csv"
        pairs_df.to_csv(out_pairs, index=False)
        print("\nStrongest pairs (mean |phi_ij|):")
        print(pairs_df.head(10).to_string(index=False))
        print(f"  Saved {out_pairs.name}")
    except Exception as e:
        print(f"  True interaction heatmap skipped: {e}")

    print("\n" + "=" * 70)
    print("DONE — Interaction artifacts written to reports/")
    print("=" * 70)


if __name__ == "__main__":
    main()
