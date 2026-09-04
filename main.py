"""
End-to-end pipeline: data -> features -> train -> evaluate -> explain -> impact
Run with: python main.py
"""
import subprocess
import sys

STEPS = [
    ("Generating data", "data/generate_synthetic_data.py"),
    ("Training models", "src/train_models.py"),
    ("Evaluating models", "src/evaluate.py"),
    ("Running SHAP explainability", "src/explainability.py"),
    ("Simulating cost/impact", "src/cost_impact.py"),
]

if __name__ == "__main__":
    for label, script in STEPS:
        print(f"\n{'='*60}\n{label}\n{'='*60}")
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"FAILED at step: {label}")
            sys.exit(1)
    print(f"\n{'='*60}\nPipeline complete. See outputs/ for all results.\n{'='*60}")
