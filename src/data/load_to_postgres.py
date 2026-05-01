from __future__ import annotations

import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

VIDEOS_PATH = "data/processed/youtube_videos.parquet"
DELIVERY_PATH = "data/synthetic_delivery/delivery_events.parquet"


def main():
    engine = create_engine(DATABASE_URL)

    print("Loading videos...")
    videos = pd.read_parquet(VIDEOS_PATH)
    videos.to_sql("videos", engine, if_exists="append", index=False)

    print("Loading delivery events...")
    events = pd.read_parquet(DELIVERY_PATH)
    events.to_sql("delivery_events", engine, if_exists="append", index=False)

    print("Done.")


if __name__ == "__main__":
    main()