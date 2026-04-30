from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from tqdm import tqdm


load_dotenv()

RAW_DIR = Path("data/raw/youtube")
PROCESSED_DIR = Path("data/processed")
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def get_youtube_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("Missing YOUTUBE_API_KEY in .env")
    return build("youtube", "v3", developerKey=api_key)


def fetch_trending_videos(youtube, region_code: str, max_pages: int = 3) -> list[dict[str, Any]]:
    items = []
    next_page_token = None

    for _ in tqdm(range(max_pages), desc=f"Fetching {region_code}"):
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()
        items.extend(response.get("items", []))

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return items


def flatten_video(item: dict[str, Any], region_code: str) -> dict[str, Any]:
    snippet = item.get("snippet", {})
    statistics = item.get("statistics", {})
    content_details = item.get("contentDetails", {})

    return {
        "video_id": item.get("id"),
        "region_code": region_code,
        "channel_id": snippet.get("channelId"),
        "channel_title": snippet.get("channelTitle"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "tags": json.dumps(snippet.get("tags", []), ensure_ascii=False),
        "category_id": snippet.get("categoryId"),
        "published_at": snippet.get("publishedAt"),
        "duration": content_details.get("duration"),
        "view_count": int(statistics.get("viewCount", 0)),
        "like_count": int(statistics.get("likeCount", 0)),
        "comment_count": int(statistics.get("commentCount", 0)),
    }


def main():
    youtube = get_youtube_client()

    regions = ["AU", "US", "SG", "JP", "KR"]
    all_rows = []

    for region in regions:
        raw_items = fetch_trending_videos(youtube, region)

        raw_path = RAW_DIR / f"trending_{region}.json"
        with raw_path.open("w", encoding="utf-8") as f:
            json.dump(raw_items, f, ensure_ascii=False, indent=2)

        rows = [flatten_video(item, region) for item in raw_items]
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["video_id", "region_code"])

    csv_path = PROCESSED_DIR / "youtube_videos.csv"
    parquet_path = PROCESSED_DIR / "youtube_videos.parquet"

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(df.shape)
    print(df.head())
    print(f"Saved CSV to {csv_path}")
    print(f"Saved Parquet to {parquet_path}")


if __name__ == "__main__":
    main()