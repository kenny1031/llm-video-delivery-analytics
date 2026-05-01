-- Average latency（A/B test）
SELECT
    variant,
    AVG(latency_ms) AS avg_latency,
    AVG(startup_time_ms) AS avg_startup,
    AVG(rebuffer_ratio) AS avg_rebuffer
FROM delivery_events
GROUP BY variant;