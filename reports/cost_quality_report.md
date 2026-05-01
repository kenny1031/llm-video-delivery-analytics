# Cost and Quality Governance Report

## Overall Summary

- Treatment latency changed by **-10.01%** (33.81 ms → 30.42 ms).
- Treatment startup time changed by **-10.05%** (54.10 ms → 48.67 ms).
- Treatment rebuffer ratio changed by **-10.01%** (0.0909 → 0.0818).
- Treatment cost per 1K events changed by **0.33%** ($0.5989 → $0.6009).
- Cache hit rate remained stable (80.05% → 80.01%).

## Regions with Highest Cost Increase

- AU: cost per 1K events changed by 2.23%, while latency changed by -10.11%.
- KR: cost per 1K events changed by 1.80%, while latency changed by -10.50%.
- US: cost per 1K events changed by -0.03%, while latency changed by -9.77%.

## Edge PoPs with Highest Cost Increase

- SJC: cost per 1K events changed by 6.96%, while latency changed by -9.76%.
- MEL: cost per 1K events changed by 2.45%, while latency changed by -10.28%.
- SYD: cost per 1K events changed by 2.00%, while latency changed by -9.95%.

## Governance Interpretation

The treatment improves delivery quality, but cost remains a guardrail metric. Because cache hit rate is broadly stable, the quality improvement is not clearly explained by cache efficiency alone. During rollout, the system should monitor whether cost increases are concentrated in specific regions or edge PoPs.