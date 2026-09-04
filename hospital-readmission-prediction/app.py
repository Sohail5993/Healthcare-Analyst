"""
Streamlit Demo – Hospital 30-Day Readmission Risk
=================================================
Simple interactive app that loads the trained pipeline and lets users
explore predicted 30-day readmission risk for a custom patient profile.

Run from project root:
    streamlit run app.py
"""

from __future__ import annotations

import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="30-Day Readmission Risk | Aimms Consuting",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 1.9rem; font-weight: 700; color: #1a365d; margin-bottom: 0.2rem; }
    .sub-title  { font-size: 1.05rem; color: #4a5568; margin-bottom: 1.2rem; }
    .risk-high  { color: #c53030; font-weight: 700; }
    .risk-med   { color: #c05600; font-weight: 700; }
    .risk-low   { color: #276749; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "best_readmission_model.joblib"

# -----------------------------------------------------------------------------
# Load model (cached)
# -----------------------------------------------------------------------------
@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        st.error(
            f"Model not found at `{MODEL_PATH}`.\n\n"
            "Please run the training pipeline first:\n"
            "```\npython src/train_pipeline.py\n```"
        )
        st.stop()
    return joblib.load(MODEL_PATH)


pipe = load_model()

# -----------------------------------------------------------------------------
# Feature engineering (must match training)
# -----------------------------------------------------------------------------
def engineer_features(raw: dict) -> pd.DataFrame:
    """Convert UI inputs into the same feature frame used at training time."""
    row = raw.copy()

    # Age → numeric (same logic as train_pipeline)
    age_str = str(row.pop("age"))
    if "younger" in age_str.lower():
        age_num = 25.0
    elif "over 60" in age_str.lower() or "older" in age_str.lower():
        age_num = 70.0
    else:
        m = re.search(r"(\d+)", age_str)
        age_num = float(m.group(1)) if m else 55.0
    row["age_numeric"] = age_num

    # Utilization score
    row["utilization_score"] = (
        float(row.get("num_lab_procedures", 0))
        + float(row.get("num_procedures", 0)) * 2
        + float(row.get("num_medications", 0))
    )

    # Booleans / categories that were stored as category in the original data
    for col in ["medicare", "medicaid", "had_emergency", "had_inpatient_days", "had_outpatient_days"]:
        if col in row:
            # Training data uses string categories "True" / "False"
            row[col] = "True" if bool(row[col]) else "False"

    df = pd.DataFrame([row])
    # Ensure column order is not critical (ColumnTransformer selects by name)
    return df


def risk_label(p: float) -> tuple[str, str]:
    if p >= 0.35:
        return "HIGH", "risk-high"
    if p >= 0.15:
        return "MEDIUM", "risk-med"
    return "LOW", "risk-low"


# -----------------------------------------------------------------------------
# Driver / explanation helpers
# -----------------------------------------------------------------------------
try:
    import shap

    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


# Human-readable labels for UI features we can perturb
PERTURB_SPECS = [
    # (raw_key, display_name, low_value, high_value)  — values are in UI/raw space
    ("time_in_hospital", "Days in hospital", 2, 10),
    ("num_lab_procedures", "Lab procedures", 15, 60),
    ("num_procedures", "Procedures", 0, 3),
    ("num_medications", "Medications", 5, 25),
    ("number_diagnoses", "Number of diagnoses", 3, 12),
    ("had_inpatient_days", "Prior inpatient days", False, True),
    ("had_emergency", "Prior emergency visit", False, True),
    ("had_outpatient_days", "Prior outpatient days", False, True),
    ("medicare", "Medicare", False, True),
    ("discharge_disposition_id", "Discharge disposition", "'Discharged to Home'", "Other"),
    ("admission_source_id", "Admission source", "Referral", "Emergency"),
    ("primary_diagnosis", "Primary diagnosis", "Other", "Diabetes"),
    ("insulin", "Insulin", "No", "Up"),
    ("A1Cresult", "A1C result", "None", ">8"),
    ("diabetesMed", "On diabetes meds", "No", "Yes"),
    ("age", "Age group", "'30-60 years'", "'Over 60 years'"),
]


def sensitivity_drivers(raw: dict, base_proba: float, top_n: int = 8) -> pd.DataFrame:
    """
    Approximate local drivers by flipping each key feature to a contrasting value
    and measuring the change in predicted probability.
    Always available (no SHAP required).
    """
    rows = []
    for key, label, low_val, high_val in PERTURB_SPECS:
        current = raw.get(key)
        # Choose the opposite pole from current
        try:
            if isinstance(low_val, bool) or isinstance(high_val, bool):
                alt = not bool(current)
            elif current == low_val:
                alt = high_val
            elif current == high_val:
                alt = low_val
            else:
                # Prefer high-risk-ish pole for numeric when in the middle
                if isinstance(low_val, (int, float)) and isinstance(high_val, (int, float)):
                    alt = high_val if float(current) <= (float(low_val) + float(high_val)) / 2 else low_val
                else:
                    alt = high_val
        except Exception:
            continue

        if alt == current:
            continue

        modified = dict(raw)
        modified[key] = alt
        try:
            X_mod = engineer_features(modified)
            p_mod = float(pipe.predict_proba(X_mod)[0, 1])
            delta = p_mod - base_proba
            rows.append(
                {
                    "Feature": label,
                    "Current": current,
                    "Alternative": alt,
                    "Δ Probability": delta,
                    "Direction": "↑ raises risk" if delta > 0 else "↓ lowers risk",
                }
            )
        except Exception:
            continue

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["|Δ|"] = df["Δ Probability"].abs()
    df = df.sort_values("|Δ|", ascending=False).head(top_n).drop(columns=["|Δ|"])
    return df.reset_index(drop=True)


def shap_local_drivers(X_user: pd.DataFrame, top_n: int = 10) -> pd.DataFrame | None:
    """Return top local SHAP drivers if the shap package is available."""
    if not HAS_SHAP:
        return None
    try:
        clf = pipe.named_steps["clf"]
        prep = pipe.named_steps["prep"]
        X_trans = prep.transform(X_user)
        feature_names = list(prep.get_feature_names_out())

        # TreeExplainer for Random Forest / XGBoost
        explainer = shap.TreeExplainer(clf)
        sv = explainer.shap_values(X_trans)
        if isinstance(sv, list):
            sv = sv[1]  # positive class
        values = np.array(sv).reshape(-1)

        df = pd.DataFrame(
            {
                "Feature": feature_names,
                "SHAP value": values,
            }
        )
        df["Direction"] = df["SHAP value"].apply(
            lambda v: "↑ raises risk" if v > 0 else "↓ lowers risk"
        )
        df["|SHAP|"] = df["SHAP value"].abs()
        df = df.sort_values("|SHAP|", ascending=False).head(top_n).drop(columns=["|SHAP|"])
        # Clean feature names for display
        df["Feature"] = (
            df["Feature"]
            .str.replace("num__", "", regex=False)
            .str.replace("cat__", "", regex=False)
        )
        return df.reset_index(drop=True)
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Preset profiles
# -----------------------------------------------------------------------------
PRESETS = {
    "Custom": None,
    "Lower-risk profile": {
        "race": "Caucasian",
        "gender": "Female",
        "age": "'30-60 years'",
        "discharge_disposition_id": "'Discharged to Home'",
        "admission_source_id": "Referral",
        "time_in_hospital": 3,
        "medical_specialty": "InternalMedicine",
        "num_lab_procedures": 25,
        "num_procedures": 0,
        "num_medications": 8,
        "primary_diagnosis": "Other",
        "number_diagnoses": 4,
        "max_glu_serum": "None",
        "A1Cresult": "None",
        "insulin": "No",
        "change": "No",
        "diabetesMed": "No",
        "medicare": False,
        "medicaid": False,
        "had_emergency": False,
        "had_inpatient_days": False,
        "had_outpatient_days": False,
    },
    "Higher-risk profile": {
        "race": "AfricanAmerican",
        "gender": "Male",
        "age": "'Over 60 years'",
        "discharge_disposition_id": "Other",
        "admission_source_id": "Emergency",
        "time_in_hospital": 8,
        "medical_specialty": "Emergency/Trauma",
        "num_lab_procedures": 55,
        "num_procedures": 2,
        "num_medications": 22,
        "primary_diagnosis": "Diabetes",
        "number_diagnoses": 9,
        "max_glu_serum": ">200",
        "A1Cresult": ">8",
        "insulin": "Up",
        "change": "Ch",
        "diabetesMed": "Yes",
        "medicare": True,
        "medicaid": False,
        "had_emergency": True,
        "had_inpatient_days": True,
        "had_outpatient_days": True,
    },
}

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 🏥 Readmission Risk Demo")
st.sidebar.markdown("Predict 30-day hospital readmission risk for a patient profile.")
st.sidebar.markdown("---")

preset_name = st.sidebar.selectbox("Load preset profile", list(PRESETS.keys()))
base = PRESETS[preset_name] or {}

st.sidebar.markdown("### Adjust key features")

# --- Demographics & admission ---
race = st.sidebar.selectbox(
    "Race",
    ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other", "Unknown"],
    index=["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other", "Unknown"].index(
        base.get("race", "Caucasian")
    ),
)
gender = st.sidebar.selectbox(
    "Gender",
    ["Female", "Male", "Unknown/Invalid"],
    index=["Female", "Male", "Unknown/Invalid"].index(base.get("gender", "Female")),
)
age = st.sidebar.selectbox(
    "Age group",
    ["'30 years or younger'", "'30-60 years'", "'Over 60 years'"],
    index=["'30 years or younger'", "'30-60 years'", "'Over 60 years'"].index(
        base.get("age", "'30-60 years'")
    ),
)
discharge = st.sidebar.selectbox(
    "Discharge disposition",
    ["'Discharged to Home'", "Other"],
    index=0 if base.get("discharge_disposition_id", "'Discharged to Home'") == "'Discharged to Home'" else 1,
)
admission_source = st.sidebar.selectbox(
    "Admission source",
    ["Emergency", "Referral", "Other"],
    index=["Emergency", "Referral", "Other"].index(base.get("admission_source_id", "Emergency")),
)

# --- Utilization ---
st.sidebar.markdown("### Utilization")
time_in_hospital = st.sidebar.slider("Days in hospital", 1, 14, int(base.get("time_in_hospital", 4)))
num_lab = st.sidebar.slider("Lab procedures", 0, 120, int(base.get("num_lab_procedures", 40)))
num_proc = st.sidebar.slider("Procedures", 0, 6, int(base.get("num_procedures", 1)))
num_meds = st.sidebar.slider("Medications", 1, 50, int(base.get("num_medications", 12)))
num_diag = st.sidebar.slider("Number of diagnoses", 1, 16, int(base.get("number_diagnoses", 6)))

# --- Clinical ---
st.sidebar.markdown("### Clinical indicators")
specialty = st.sidebar.selectbox(
    "Medical specialty",
    ["Missing", "Other", "InternalMedicine", "Emergency/Trauma", "Family/GeneralPractice", "Cardiology"],
    index=0,
)
primary_dx = st.sidebar.selectbox(
    "Primary diagnosis group",
    ["Other", "Diabetes", "'Respiratory Issues'", "'Genitourinary Issues'", "'Circulatory Issues'"],
    index=0 if base.get("primary_diagnosis", "Other") == "Other" else 1,
)
max_glu = st.sidebar.selectbox("Max glucose serum", ["None", "Norm", ">200", ">300"], index=0)
a1c = st.sidebar.selectbox("A1C result", ["None", "Norm", ">7", ">8"], index=0)
insulin = st.sidebar.selectbox("Insulin", ["No", "Steady", "Down", "Up"], index=0)
change = st.sidebar.selectbox("Med change", ["No", "Ch"], index=0)
diabetes_med = st.sidebar.selectbox("On diabetes meds", ["No", "Yes"], index=1 if base.get("diabetesMed") == "Yes" else 0)

# --- History flags ---
st.sidebar.markdown("### Prior utilization flags")
medicare = st.sidebar.checkbox("Medicare", value=bool(base.get("medicare", False)))
medicaid = st.sidebar.checkbox("Medicaid", value=bool(base.get("medicaid", False)))
had_emergency = st.sidebar.checkbox("Had emergency visit (prior year)", value=bool(base.get("had_emergency", False)))
had_inpatient = st.sidebar.checkbox("Had inpatient days (prior year)", value=bool(base.get("had_inpatient_days", False)))
had_outpatient = st.sidebar.checkbox("Had outpatient days (prior year)", value=bool(base.get("had_outpatient_days", False)))

# -----------------------------------------------------------------------------
# Build input & predict
# -----------------------------------------------------------------------------
raw_input = {
    "race": race,
    "gender": gender,
    "age": age,
    "discharge_disposition_id": discharge,
    "admission_source_id": admission_source,
    "time_in_hospital": time_in_hospital,
    "medical_specialty": specialty,
    "num_lab_procedures": num_lab,
    "num_procedures": num_proc,
    "num_medications": num_meds,
    "primary_diagnosis": primary_dx,
    "number_diagnoses": num_diag,
    "max_glu_serum": max_glu,
    "A1Cresult": a1c,
    "insulin": insulin,
    "change": change,
    "diabetesMed": diabetes_med,
    "medicare": medicare,
    "medicaid": medicaid,
    "had_emergency": had_emergency,
    "had_inpatient_days": had_inpatient,
    "had_outpatient_days": had_outpatient,
}

X_user = engineer_features(raw_input)

try:
    proba = float(pipe.predict_proba(X_user)[0, 1])
except Exception as e:
    st.error(f"Prediction failed: {e}")
    st.stop()

tier, css_class = risk_label(proba)

# -----------------------------------------------------------------------------
# Main panel
# -----------------------------------------------------------------------------
st.markdown('<p class="main-title">🏥 30-Day Hospital Readmission Risk</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Interactive demo of the trained Random Forest / pipeline model. '
    "Adjust features in the sidebar or load a preset.</p>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Predicted probability", f"{proba:.1%}")
with col2:
    st.markdown(f"**Risk tier**  \n<span class='{css_class}'>{tier}</span>", unsafe_allow_html=True)
with col3:
    st.metric("Model", "Random Forest (best)")

st.progress(min(max(proba, 0.0), 1.0))

st.markdown("---")

# Interpretation guidance
st.subheader("How to read this score")
if tier == "HIGH":
    st.warning(
        "This profile is flagged as **higher risk** of 30-day readmission. "
        "In a real hospital setting this would typically trigger enhanced discharge planning, "
        "early follow-up appointments, or care-management outreach."
    )
elif tier == "MEDIUM":
    st.info(
        "This profile sits in a **medium-risk** band. Clinical judgment and additional context "
        "(social support, medication adherence, etc.) would normally guide the intensity of follow-up."
    )
else:
    st.success(
        "This profile is predicted as **lower risk**. Standard discharge processes would usually apply, "
        "while still watching for any new clinical changes."
    )

# -----------------------------------------------------------------------------
# Driver list (SHAP if available, else sensitivity-based)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("What is driving this risk score?")

shap_df = shap_local_drivers(X_user, top_n=10)
sens_df = sensitivity_drivers(raw_input, proba, top_n=8)

tab_shap, tab_sens = st.tabs(
    [
        "SHAP local drivers" + (" ✓" if shap_df is not None else " (package not installed)"),
        "Sensitivity drivers (always available)",
    ]
)

with tab_shap:
    if shap_df is not None and len(shap_df) > 0:
        st.caption(
            "SHAP values for this patient. Positive values push the prediction toward higher "
            "30-day readmission risk; negative values push it lower."
        )
        # Color the SHAP column
        st.dataframe(
            shap_df.style.format({"SHAP value": "{:+.4f}"}).apply(
                lambda s: [
                    "color: #c53030" if v > 0 else "color: #276749"
                    for v in s
                ]
                if s.name == "SHAP value"
                else [""] * len(s),
                axis=0,
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Top transformed features from the model pipeline (One-Hot + scaled numerics).")
    else:
        st.info(
            "SHAP is not installed in this environment, so local SHAP values are unavailable. "
            "Install with `pip install shap` and restart the app to enable this tab. "
            "Use the **Sensitivity drivers** tab in the meantime — it works without SHAP."
        )

with tab_sens:
    st.caption(
        "Each row shows how the predicted probability would change if that feature were set to a "
        "contrasting value (holding everything else fixed). This is a simple, model-agnostic way "
        "to surface drivers when SHAP is not available."
    )
    if sens_df is not None and len(sens_df) > 0:
        st.dataframe(
            sens_df.style.format({"Δ Probability": "{:+.3f}"}).apply(
                lambda s: [
                    "color: #c53030" if v > 0 else "color: #276749"
                    for v in s
                ]
                if s.name == "Δ Probability"
                else [""] * len(s),
                axis=0,
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("Could not compute sensitivity drivers for this profile.")

# Feature summary
with st.expander("View current patient feature vector"):
    st.dataframe(X_user.T.rename(columns={0: "Value"}), use_container_width=True)

st.markdown("---")
st.caption(
    "**Disclaimer:** This is an educational / portfolio demonstration only. "
    "It is **not** a clinical decision-support system and must not be used for real patient care. "
    "The underlying model was trained on the public Diabetes 130-US Hospitals dataset (1999–2008)."
)

st.sidebar.markdown("---")
st.sidebar.caption("Aimms Consuting · Strategic Foresighted Semantic BI Analyst")
st.sidebar.caption("“Let’s Color The Daring Dreams Together”")
