from __future__ import annotations
import os
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OUTPUT_DIR = Path("reports/diagnostics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_sql(query: str) -> pd.DataFrame:
    if not DATABASE_URL:
        raise ValueError("Missing DATABASE_URL in .env")

    engine = create_engine(DATABASE_URL)
    return pd.read_sql(query, engine)


def segment_query(segment_col: str) -> str:
    return f"""
    SELECT
        {segment_col},
        variant,
        COUNT(*) AS event_count,
        AVG(latency_ms) AS avg_latency_ms,
        AVG(startup_time_ms) AS avg_startup_time_ms,
        AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
        AVG(cache_hit) AS cache_hit_rate,
        SUM(cdn_cost_usd) AS total_cdn_cost_usd
    FROM delivery_events
    GROUP BY {segment_col}, variant
    ORDER BY avg_latency_ms DESC
    """


def compute_treatment_gap(df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    pivot = df.pivot(index=segment_col, columns="variant")

    out = pd.DataFrame({
        segment_col: pivot.index,
        "control_latency_ms": pivot["avg_latency_ms"]["control"],
        "treatment_latency_ms": pivot["avg_latency_ms"]["treatment"],
        "latency_diff_ms": pivot["avg_latency_ms"]["treatment"] - pivot["avg_latency_ms"]["control"],
        "control_startup_ms": pivot["avg_startup_time_ms"]["control"],
        "treatment_startup_ms": pivot["avg_startup_time_ms"]["treatment"],
        "startup_diff_ms": pivot["avg_startup_time_ms"]["treatment"] - pivot["avg_startup_time_ms"]["control"],
        "control_rebuffer": pivot["avg_rebuffer_ratio"]["control"],
        "treatment_rebuffer": pivot["avg_rebuffer_ratio"]["treatment"],
        "rebuffer_diff": pivot["avg_rebuffer_ratio"]["treatment"] - pivot["avg_rebuffer_ratio"]["control"],
        "control_cache_hit_rate": pivot["cache_hit_rate"]["control"],
        "treatment_cache_hit_rate": pivot["cache_hit_rate"]["treatment"],
        "treatment_total_cost_usd": pivot["total_cdn_cost_usd"]["treatment"],
        "control_total_cost_usd": pivot["total_cdn_cost_usd"]["control"],
    }).reset_index(drop=True)

    out["latency_lift_pct"] = out["latency_diff_ms"] / out["control_latency_ms"] * 100
    out["startup_lift_pct"] = out["startup_diff_ms"] / out["control_startup_ms"] * 100
    out["rebuffer_lift_pct"] = out["rebuffer_diff"] / out["control_rebuffer"] * 100
    out["cost_diff_usd"] = out["treatment_total_cost_usd"] - out["control_total_cost_usd"]

    return out.sort_values("latency_diff_ms")


def main() -> None:
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    segments = ["region_code", "edge_pop", "protocol", "ip_version"]

    summary = {}

    for segment in segments:
        df = read_sql(segment_query(segment))
        gap = compute_treatment_gap(df, segment)

        csv_path = OUTPUT_DIR / f"{segment}_diagnostics.csv"
        gap.to_csv(csv_path, index=False)

        summary[segment] = gap.head(5).to_dict(orient="records")

        print(f"\n=== {segment} diagnostics ===")
        print(gap)

    json_path = OUTPUT_DIR / "root_cause_summary.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved diagnostics to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()