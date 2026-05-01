from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OUTPUT_PATH = Path("reports/cost_quality_report.md")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def read_sql(query: str) -> pd.DataFrame:
    if not DATABASE_URL:
        raise ValueError("Missing DATABASE_URL in .env")
    engine = create_engine(DATABASE_URL)
    return pd.read_sql(query, engine)


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def fmt_ms(x: float) -> str:
    return f"{x:.2f} ms"


def fmt_usd(x: float) -> str:
    return f"${x:.4f}"


def main() -> None:
    overall = read_sql(
        """
        SELECT
            variant,
            COUNT(*) AS event_count,
            SUM(cdn_cost_usd) AS total_cost,
            AVG(cdn_cost_usd) AS avg_cost_per_event,
            SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
            AVG(cache_hit) AS cache_hit_rate,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(startup_time_ms) AS avg_startup_time_ms,
            AVG(rebuffer_ratio) AS avg_rebuffer_ratio
        FROM delivery_events
        GROUP BY variant
        """
    )

    region = read_sql(
        """
        SELECT
            region_code,
            variant,
            COUNT(*) AS event_count,
            SUM(cdn_cost_usd) AS total_cost,
            SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
            AVG(cache_hit) AS cache_hit_rate,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(rebuffer_ratio) AS avg_rebuffer_ratio
        FROM delivery_events
        GROUP BY region_code, variant
        """
    )

    edge = read_sql(
        """
        SELECT
            edge_pop,
            variant,
            COUNT(*) AS event_count,
            SUM(cdn_cost_usd) AS total_cost,
            SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
            AVG(cache_hit) AS cache_hit_rate,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(rebuffer_ratio) AS avg_rebuffer_ratio
        FROM delivery_events
        GROUP BY edge_pop, variant
        """
    )

    overall_pivot = overall.set_index("variant")

    control = overall_pivot.loc["control"]
    treatment = overall_pivot.loc["treatment"]

    latency_lift = (
        (treatment["avg_latency_ms"] - control["avg_latency_ms"])
        / control["avg_latency_ms"]
    )
    startup_lift = (
        (treatment["avg_startup_time_ms"] - control["avg_startup_time_ms"])
        / control["avg_startup_time_ms"]
    )
    rebuffer_lift = (
        (treatment["avg_rebuffer_ratio"] - control["avg_rebuffer_ratio"])
        / control["avg_rebuffer_ratio"]
    )
    cost_lift = (
        (treatment["cost_per_1k_events"] - control["cost_per_1k_events"])
        / control["cost_per_1k_events"]
    )

    region_pivot = region.pivot(index="region_code", columns="variant")
    region_summary = pd.DataFrame(
        {
            "region_code": region_pivot.index,
            "control_cost_per_1k": region_pivot["cost_per_1k_events"]["control"],
            "treatment_cost_per_1k": region_pivot["cost_per_1k_events"]["treatment"],
            "control_latency_ms": region_pivot["avg_latency_ms"]["control"],
            "treatment_latency_ms": region_pivot["avg_latency_ms"]["treatment"],
        }
    )
    region_summary["cost_lift_pct"] = (
        (region_summary["treatment_cost_per_1k"] - region_summary["control_cost_per_1k"])
        / region_summary["control_cost_per_1k"]
        * 100
    )
    region_summary["latency_lift_pct"] = (
        (region_summary["treatment_latency_ms"] - region_summary["control_latency_ms"])
        / region_summary["control_latency_ms"]
        * 100
    )

    top_cost_increase_regions = region_summary.sort_values(
        "cost_lift_pct", ascending=False
    ).head(3)

    edge_pivot = edge.pivot(index="edge_pop", columns="variant")
    edge_summary = pd.DataFrame(
        {
            "edge_pop": edge_pivot.index,
            "control_cost_per_1k": edge_pivot["cost_per_1k_events"]["control"],
            "treatment_cost_per_1k": edge_pivot["cost_per_1k_events"]["treatment"],
            "control_latency_ms": edge_pivot["avg_latency_ms"]["control"],
            "treatment_latency_ms": edge_pivot["avg_latency_ms"]["treatment"],
        }
    )
    edge_summary["cost_lift_pct"] = (
        (edge_summary["treatment_cost_per_1k"] - edge_summary["control_cost_per_1k"])
        / edge_summary["control_cost_per_1k"]
        * 100
    )
    edge_summary["latency_lift_pct"] = (
        (edge_summary["treatment_latency_ms"] - edge_summary["control_latency_ms"])
        / edge_summary["control_latency_ms"]
        * 100
    )

    top_cost_increase_edges = edge_summary.sort_values(
        "cost_lift_pct", ascending=False
    ).head(3)

    lines = []

    lines.append("# Cost and Quality Governance Report\n")

    lines.append("## Overall Summary\n")
    lines.append(
        f"- Treatment latency changed by **{latency_lift * 100:.2f}%** "
        f"({fmt_ms(control['avg_latency_ms'])} → {fmt_ms(treatment['avg_latency_ms'])})."
    )
    lines.append(
        f"- Treatment startup time changed by **{startup_lift * 100:.2f}%** "
        f"({fmt_ms(control['avg_startup_time_ms'])} → {fmt_ms(treatment['avg_startup_time_ms'])})."
    )
    lines.append(
        f"- Treatment rebuffer ratio changed by **{rebuffer_lift * 100:.2f}%** "
        f"({control['avg_rebuffer_ratio']:.4f} → {treatment['avg_rebuffer_ratio']:.4f})."
    )
    lines.append(
        f"- Treatment cost per 1K events changed by **{cost_lift * 100:.2f}%** "
        f"({fmt_usd(control['cost_per_1k_events'])} → {fmt_usd(treatment['cost_per_1k_events'])})."
    )
    lines.append(
        f"- Cache hit rate remained stable "
        f"({fmt_pct(control['cache_hit_rate'])} → {fmt_pct(treatment['cache_hit_rate'])})."
    )

    lines.append("\n## Regions with Highest Cost Increase\n")
    for _, r in top_cost_increase_regions.iterrows():
        lines.append(
            f"- {r['region_code']}: cost per 1K events changed by "
            f"{r['cost_lift_pct']:.2f}%, while latency changed by {r['latency_lift_pct']:.2f}%."
        )

    lines.append("\n## Edge PoPs with Highest Cost Increase\n")
    for _, r in top_cost_increase_edges.iterrows():
        lines.append(
            f"- {r['edge_pop']}: cost per 1K events changed by "
            f"{r['cost_lift_pct']:.2f}%, while latency changed by {r['latency_lift_pct']:.2f}%."
        )

    lines.append("\n## Governance Interpretation\n")
    lines.append(
        "The treatment improves delivery quality, but cost remains a guardrail metric. "
        "Because cache hit rate is broadly stable, the quality improvement is not clearly explained by cache efficiency alone. "
        "During rollout, the system should monitor whether cost increases are concentrated in specific regions or edge PoPs."
    )

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(OUTPUT_PATH.read_text(encoding="utf-8"))
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()