from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_PATH = Path("data/synthetic_delivery/edge_capacity_snapshots.parquet")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


EDGE_META = {
    "SYD": {"region_code": "AU", "max_capacity_mbps": 9000},
    "MEL": {"region_code": "AU", "max_capacity_mbps": 7500},
    "SIN": {"region_code": "SG", "max_capacity_mbps": 14000},
    "NRT": {"region_code": "JP", "max_capacity_mbps": 8500},
    "ICN": {"region_code": "KR", "max_capacity_mbps": 7000},
    "LAX": {"region_code": "US", "max_capacity_mbps": 12000},
    "SJC": {"region_code": "US", "max_capacity_mbps": 11000},
}


def simulate_hourly_capacity(days: int = 14, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(
        end=pd.Timestamp.utcnow().floor("h"),
        periods=days * 24,
        freq="h",
    )

    rows = []

    for ts in timestamps:
        hour = ts.hour

        # simple daily traffic curve: busier during evening
        daily_factor = 0.55 + 0.25 * np.sin((hour - 8) / 24 * 2 * np.pi)

        for edge_pop, meta in EDGE_META.items():
            max_capacity = meta["max_capacity_mbps"]

            edge_noise = rng.normal(0, 0.06)
            utilization = np.clip(daily_factor + edge_noise, 0.25, 0.92)

            # add occasional high-utilization spikes
            if rng.random() < 0.025:
                utilization = np.clip(utilization + rng.uniform(0.12, 0.22), 0.25, 0.98)

            used_capacity = max_capacity * utilization
            active_connections = int(used_capacity * rng.uniform(8, 15))

            cpu_util = np.clip(utilization + rng.normal(0.03, 0.05), 0.1, 0.99)
            memory_util = np.clip(0.45 + 0.35 * utilization + rng.normal(0, 0.04), 0.1, 0.95)

            rows.append(
                {
                    "snapshot_time": ts.to_pydatetime(),
                    "edge_pop": edge_pop,
                    "region_code": meta["region_code"],
                    "max_capacity_mbps": max_capacity,
                    "used_capacity_mbps": used_capacity,
                    "utilization_ratio": utilization,
                    "active_connections": active_connections,
                    "cpu_utilization": cpu_util,
                    "memory_utilization": memory_util,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    df = simulate_hourly_capacity()
    df.to_parquet(OUTPUT_PATH, index=False)

    print(df.shape)
    print(df.head())
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()