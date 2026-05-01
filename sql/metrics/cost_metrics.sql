-- Cost Governance Metrics

-- 1. Overall cost by variant
SELECT
    variant,
    COUNT(*) AS event_count,
    SUM(cdn_cost_usd) AS total_cdn_cost_usd,
    AVG(cdn_cost_usd) AS avg_cost_per_event,
    SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
    AVG(cache_hit) AS cache_hit_rate,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(startup_time_ms) AS avg_startup_time_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio
FROM delivery_events
GROUP BY variant
ORDER BY variant;

-- 2. Cost by region and variant
SELECT
    region_code,
    variant,
    COUNT(*) AS event_count,
    SUM(cdn_cost_usd) AS total_cdn_cost_usd,
    SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
    AVG(cache_hit) AS cache_hit_rate,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio
FROM delivery_events
GROUP BY region_code, variant
ORDER BY total_cdn_cost_usd DESC;

-- 3. Cost by edge PoP and variant
SELECT
    edge_pop,
    variant,
    COUNT(*) AS event_count,
    SUM(cdn_cost_usd) AS total_cdn_cost_usd,
    SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
    AVG(cache_hit) AS cache_hit_rate,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio
FROM delivery_events
GROUP BY edge_pop, variant
ORDER BY total_cdn_cost_usd DESC;

-- 4. Cost-quality tradeoff by edge PoP
SELECT
    edge_pop,
    variant,
    COUNT(*) AS event_count,
    SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
    AVG(latency_ms) AS avg_latency_ms,
    AVG(startup_time_ms) AS avg_startup_time_ms,
    AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
    AVG(cache_hit) AS cache_hit_rate
FROM delivery_events
GROUP BY edge_pop, variant
ORDER BY cost_per_1k_events DESC;