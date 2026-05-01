from __future__ import annotations
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from scipy import stats
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def bootstrap_ci(control, treatment, n_bootstrap=1000):
    diffs = []
    for _ in range(n_bootstrap):
        c = np.random.choice(control, size=len(control), replace=True)
        t = np.random.choice(treatment, size=len(treatment), replace=True)
        diffs.append(np.mean(t) - np.mean(c))

    return np.percentile(diffs, [2.5, 97.5])


def main():
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql("SELECT latency_ms, variant FROM delivery_events", engine)

    control = df[df["variant"] == "control"]["latency_ms"].values
    treatment = df[df["variant"] == "treatment"]["latency_ms"].values

    mean_control = np.mean(control)
    mean_treatment = np.mean(treatment)

    lift = (mean_treatment - mean_control) / mean_control

    # t-test
    t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)

    # bootstrap CI
    ci_lower, ci_upper = bootstrap_ci(control, treatment)

    print("\n=== A/B Test Result ===")
    print(f"Control mean: {mean_control:.4f}")
    print(f"Treatment mean: {mean_treatment:.4f}")
    print(f"Lift: {lift:.4%}")
    print(f"P-value: {p_value:.6f}")
    print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

    # simple decision
    if p_value < 0.05:
        print("Result: statistically significant")
    else:
        print("Result: NOT statistically significant")


if __name__ == "__main__":
    main()