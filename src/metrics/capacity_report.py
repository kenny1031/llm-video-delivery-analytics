from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OUTPUT_PATH = Path("reports/capacity_report.md")


def read_sql(query: str) -> pd.DataFrame:
    if not DATABASE_URL:
        raise ValueError("Missing DATABASE_URL in .env")
    engine = create_engine(DATABASE_URL)
    return pd.read_sql(query, engine)


def pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def main() -> None:
    risk = read_sql(
        """
        SELECT
            edge_pop,
            region_code,
            AVG(utilization_ratio) AS avg_utilization,
            MAX(utilization_ratio) AS peak_utilization,
            SUM(CASE WHEN utilization_ratio >= 0.85 THEN 1 ELSE 0 END) AS high_utilization_hours,
            SUM(CASE WHEN utilization_ratio >= 0.90 THEN 1 ELSE 0 END) AS critical_utilization_hours,
            COUNT(*) AS total_hours,
            SUM(CASE WHEN utilization_ratio >= 0.85 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS high_utilization_share,
            AVG(cpu_utilization) AS avg_cpu_utilization,
            AVG(memory_utilization) AS avg_memory_utilization
        FROM edge_capacity_snapshots
        GROUP BY edge_pop, region_code
        ORDER BY high_utilization_share DESC, peak_utilization DESC
        """
    )

    top_risk = risk.head(3)

    lines = []
    lines.append("# Capacity and Resource Utilization Report\n")

    lines.append("## Objective\n")
    lines.append(
        "Analyze edge PoP resource capacity and identify segments that may require capacity planning during traffic growth or delivery strategy rollout.\n"
    )

    lines.append("## Highest Capacity Risk Edge PoPs\n")
    for _, r in top_risk.iterrows():
        lines.append(
            f"- {r['edge_pop']} ({r['region_code']}): peak utilization {pct(r['peak_utilization'])}, "
            f"high-utilization share {pct(r['high_utilization_share'])}, "
            f"critical hours {int(r['critical_utilization_hours'])}/{int(r['total_hours'])}."
        )

    lines.append("\n## Full Capacity Risk Table\n")
    lines.append(
        "| Edge PoP | Region | Avg Utilization | Peak Utilization | High Util Hours | Critical Hours | High Util Share | Avg CPU | Avg Memory |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")

    for _, r in risk.iterrows():
        lines.append(
            f"| {r['edge_pop']} | {r['region_code']} | {pct(r['avg_utilization'])} | "
            f"{pct(r['peak_utilization'])} | {int(r['high_utilization_hours'])} | "
            f"{int(r['critical_utilization_hours'])} | {pct(r['high_utilization_share'])} | "
            f"{pct(r['avg_cpu_utilization'])} | {pct(r['avg_memory_utilization'])} |"
        )

    lines.append("\n## Governance Interpretation\n")
    lines.append(
        "Edge PoPs with repeated high-utilization hours should be monitored during rollout. "
        "If quality improves but capacity risk increases, rollout decisions should consider both delivery quality and resource headroom."
    )

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT_PATH.read_text(encoding="utf-8"))
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()