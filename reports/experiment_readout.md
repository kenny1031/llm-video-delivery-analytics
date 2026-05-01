# Experiment Readout: Protocol Test
## Objective
Evaluate whether the treatment delivery strategy improves video delivery quality compared with the control strategy.

## Primary Metric
Average delivery latency (`latency_ms`).

## Guardrail Metrics
- Startup time (`startup_time_ms`)
- Rebuffer ratio (`rebuffer_ratio`)

## Result Summary

| Metric | Control | Treatment | Direction |
|---|---:|---:|---|
| Average latency | 33.81 ms | 30.42 ms | Improved |
| Average startup time | 54.10 ms | 48.67 ms | Improved |
| Average rebuffer ratio | 0.0909 | 0.0818 | Improved |

The treatment reduced average delivery latency by approximately **10.01%**.

The bootstrap 95% confidence interval for the latency difference was approximately:

```text
[-3.47 ms, -3.30 ms]
```

The two-sample t-test returned:
```text
p-value < 0.001
```

## Decision
The treatment strategy shows a statistically significant imrpovement in average delivery latency, while also improving startup time and rebuffer ratio.

Recommendation: continue rollout to a larger traffic segment and monitor cost, cache hit rate, and regional performance.