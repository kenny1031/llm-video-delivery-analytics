-- Capacity / Resource Utilization Metrics

-- 1. Overall edge utilization
SELECT
    edge_pop,
    region_code,
    COUNT(*) AS snapshot_count,
    AVG(utilization_ratio) AS avg_utilization,
    MAX(utilization_ratio) AS peak_utilization,
    AVG(cpu_utilization) AS avg_cpu_utilization,
    AVG(memory_utilization) AS avg_memory_utilization,
    AVG(active_connections) AS avg_active_connections
FROM edge_capacity_snapshots
GROUP BY edge_pop, region_code
ORDER BY peak_utilization DESC;

-- 2. High utilization snapshots
SELECT
    edge_pop,
    region_code,
    snapshot_time,
    utilization_ratio,
    used_capacity_mbps,
    max_capacity_mbps,
    cpu_utilization,
    memory_utilization,
    active_connections
FROM edge_capacity_snapshots
WHERE utilization_ratio >= 0.85
ORDER BY utilization_ratio DESC
LIMIT 30;

-- 3. Capacity risk summary
SELECT
    edge_pop,
    region_code,
    AVG(utilization_ratio) AS avg_utilization,
    MAX(utilization_ratio) AS peak_utilization,
    SUM(CASE WHEN utilization_ratio >= 0.85 THEN 1 ELSE 0 END) AS high_utilization_hours,
    SUM(CASE WHEN utilization_ratio >= 0.90 THEN 1 ELSE 0 END) AS critical_utilization_hours,
    COUNT(*) AS total_hours,
    SUM(CASE WHEN utilization_ratio >= 0.85 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS high_utilization_share
FROM edge_capacity_snapshots
GROUP BY edge_pop, region_code
ORDER BY high_utilization_share DESC, peak_utilization DESC;