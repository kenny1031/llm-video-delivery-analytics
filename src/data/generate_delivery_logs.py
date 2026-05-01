from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm


INPUT_PATH = Path("data/processed/youtube_videos.parquet")
OUTPUT_PATH = Path("data/synthetic_delivery/delivery_events.parquet")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


REGION_TO_POP = {
    "AU": ["SYD", "MEL"],
    "US": ["LAX", "SJC"],
    "SG": ["SIN"],
    "JP": ["NRT"],
    "KR": ["ICN"],
}

PROTOCOLS = ["TCP", "QUIC", "HTTP3"]
IP_VERSIONS = ["IPv4", "IPv6"]


def simulate_events(df: pd.DataFrame, max_events: int = 300_000):
    rows = []

    # construct weight sampling according to view_count
    weights = df["view_count"].values
    weights = weights / weights.sum()

    sampled_idx = np.random.choice(
        len(df),
        size=max_events,
        p=weights,
    )

    sampled = df.iloc[sampled_idx].reset_index(drop=True)

    for _, row in tqdm(sampled.iterrows(), total=len(sampled)):
        region = row["region_code"]

        edge_pop = np.random.choice(REGION_TO_POP.get(region, ["UNKNOWN"]))
        protocol = np.random.choice(PROTOCOLS, p=[0.4, 0.4, 0.2])
        ip_version = np.random.choice(IP_VERSIONS, p=[0.8, 0.2])

        # latency (ms)
        base_latency = {
            "AU": 40,
            "US": 60,
            "SG": 30,
            "JP": 35,
            "KR": 30,
        }.get(region, 50)

        latency = np.random.normal(base_latency, 10)
        latency = max(5, latency)

        # rebuffer ratio (0~1)
        rebuffer = np.clip(np.random.beta(2, 20), 0, 1)

        # experiment
        experiment_id = "protocol_test"
        variant = np.random.choice(["control", "treatment"])

        # treatment improves delivery quality
        if variant == "treatment":
            latency *= 0.9
            rebuffer *= 0.9

        # startup time should depend on post-treatment latency
        startup_time = latency * np.random.uniform(1.2, 2.0)

        # cache hit
        cache_hit = np.random.choice([0, 1], p=[0.2, 0.8])

        # bitrate
        bitrate = np.random.normal(3000, 800)

        # CDN cost
        cost = bitrate / 1_000_000 * (1 - cache_hit) * np.random.uniform(0.8, 1.2)

        rows.append(
            {
                "video_id": row["video_id"],
                "region_code": region,
                "edge_pop": edge_pop,
                "protocol": protocol,
                "ip_version": ip_version,
                "latency_ms": latency,
                "startup_time_ms": startup_time,
                "rebuffer_ratio": rebuffer,
                "bitrate_kbps": bitrate,
                "cache_hit": cache_hit,
                "cdn_cost_usd": cost,
                "experiment_id": experiment_id,
                "variant": variant,
            }
        )

    return pd.DataFrame(rows)


def main():
    df = pd.read_parquet(INPUT_PATH)

    print("Generating synthetic delivery events...")
    events = simulate_events(df)

    events.to_parquet(OUTPUT_PATH, index=False)

    print(events.shape)
    print(events.head())
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()