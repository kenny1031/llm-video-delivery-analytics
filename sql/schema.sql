-- Videos (content metadata)
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT,
    region_code TEXT,
    channel_id TEXT,
    channel_title TEXT,
    title TEXT,
    description TEXT,
    tags TEXT,
    category_id TEXT,
    published_at TIMESTAMP,
    duration TEXT,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    PRIMARY KEY (video_id, region_code)
);

-- Delivery Events
CREATE TABLE IF NOT EXISTS delivery_events (
    event_id BIGSERIAL PRIMARY KEY,
    video_id TEXT,
    region_code TEXT,
    edge_pop TEXT,
    protocol TEXT,
    ip_version TEXT,
    latency_ms FLOAT,
    startup_time_ms FLOAT,
    rebuffer_ratio FLOAT,
    bitrate_kbps FLOAT,
    cache_hit INT,
    cdn_cost_usd FLOAT,
    experiment_id TEXT,
    variant TEXT
);

CREATE INDEX IF NOT EXISTS idx_delivery_variant ON delivery_events(variant);
CREATE INDEX IF NOT EXISTS idx_delivery_region ON delivery_events(region_code);
CREATE INDEX IF NOT EXISTS idx_delivery_video ON delivery_events(video_id);