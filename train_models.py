"""
Model Training
===============
Trains three classifiers on the readmission task:
  1. Logistic Regression  -- interpretable baseline, clinically trusted
  2. Random Forest        -- captures non-linear interactions
  3. XGBoost              -- typically best AUC/PR-AUC for tabular EHR data

Handles class imbalance via class_weight / scale_pos_weight rather than
resampling, which tends to generalize better for this kind of tabular
clinical data and keeps probability calibration more honest.
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

import sys
sys.path.append("/home/claude/readmission_project/src")
from feature_engineering import build_feature_matrix

DATA_PATH = "/home/claude/readmission_project/data/encounters.csv"
MODEL_DIR = "/home/claude/readmission_project/outputs"


def load_data():
    raw = pd.read_csv(DATA_PATH)
    X, y = build_feature_matrix(raw)
    return X, y


def split_data(X, y, test_size=0.2, val_size=0.1, seed=42):
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=seed
    )
    val_frac = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_frac, stratify=y_temp, random_state=seed
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def train_logistic_regression(X_train, y_train, scaler):
    X_train_s = scaler.transform(X_train)
    model = LogisticRegression(
        max_iter=2000, class_weight="balanced", C=1.0, random_state=42
    )
    model.fit(X_train_s, y_train)
    return model


def train_random_forest(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=8,
        min_samples_leaf=20,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train):
    pos = y_train.sum()
    neg = len(y_train) - pos
    scale_pos_weight = neg / pos

    model = XGBClassifier(
        n_estimators=400,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        reg_lambda=1.5,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def main():
    print("Loading data & engineering features...")
    X, y = load_data()
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)
    print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")

    scaler = StandardScaler().fit(X_train)

    print("Training Logistic Regression...")
    lr = train_logistic_regression(X_train, y_train, scaler)

    print("Training Random Forest...")
    rf = train_random_forest(X_train, y_train)

    print("Training XGBoost...")
    xgb = train_xgboost(X_train, y_train)

    joblib.dump(
        {
            "logistic_regression": lr,
            "random_forest": rf,
            "xgboost": xgb,
            "scaler": scaler,
            "feature_names": list(X.columns),
            "splits": {
                "X_train": X_train, "X_val": X_val, "X_test": X_test,
                "y_train": y_train, "y_val": y_val, "y_test": y_test,
            },
        },
        f"{MODEL_DIR}/models_and_splits.joblib",
    )
    print(f"Saved models + data splits -> {MODEL_DIR}/models_and_splits.joblib")


if __name__ == "__main__":
    main()
