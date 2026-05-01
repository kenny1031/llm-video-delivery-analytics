-- Segment-level delivery quality diagnostics

-- 1. Region-level quality
SELECT
    region_code,
    variant,
    COUNT(*) AS event_count,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(startup_time_ms) AS avg_startup_time_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
    AVG(cache_hit) AS cache_hit_rate,
    SUM(cdn_cost_usd) AS total_cdn_cost_usd
FROM delivery_events
GROUP BY region_code, variant
ORDER BY avg_latency_ms DESC;


-- 2. Edge PoP-level quality
SELECT
    edge_pop,
    variant,
    COUNT(*) AS event_count,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(startup_time_ms) AS avg_startup_time_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
    AVG(cache_hit) AS cache_hit_rate,
    SUM(cdn_cost_usd) AS total_cdn_cost_usd
FROM delivery_events
GROUP BY edge_pop, variant
ORDER BY avg_latency_ms DESC;


-- 3. Protocol-level quality
SELECT
    protocol,
    variant,
    COUNT(*) AS event_count,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(startup_time_ms) AS avg_startup_time_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
    AVG(cache_hit) AS cache_hit_rate,
    SUM(cdn_cost_usd) AS total_cdn_cost_usd
FROM delivery_events
GROUP BY protocol, variant
ORDER BY avg_latency_ms DESC;


-- 4. IP version-level quality
SELECT
    ip_version,
    variant,
    COUNT(*) AS event_count,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(startup_time_ms) AS avg_startup_time_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
    AVG(cache_hit) AS cache_hit_rate,
    SUM(cdn_cost_usd) AS total_cdn_cost_usd
FROM delivery_events
GROUP BY ip_version, variant
ORDER BY avg_latency_ms DESC;