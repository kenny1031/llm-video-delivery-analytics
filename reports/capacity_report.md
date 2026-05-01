# Capacity and Resource Utilization Report

## Objective

Analyze edge PoP resource capacity and identify segments that may require capacity planning during traffic growth or delivery strategy rollout.

## Highest Capacity Risk Edge PoPs

- SIN (SG): peak utilization 98.00%, high-utilization share 5.36%, critical hours 3/336.
- MEL (AU): peak utilization 98.00%, high-utilization share 4.17%, critical hours 6/336.
- SYD (AU): peak utilization 98.00%, high-utilization share 4.17%, critical hours 3/336.

## Full Capacity Risk Table

| Edge PoP | Region | Avg Utilization | Peak Utilization | High Util Hours | Critical Hours | High Util Share | Avg CPU | Avg Memory |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| SIN | SG | 55.42% | 98.00% | 18 | 3 | 5.36% | 58.18% | 64.22% |
| MEL | AU | 55.41% | 98.00% | 14 | 6 | 4.17% | 57.65% | 64.28% |
| SYD | AU | 55.32% | 98.00% | 14 | 3 | 4.17% | 58.06% | 64.31% |
| LAX | US | 55.78% | 92.00% | 13 | 4 | 3.87% | 58.76% | 64.48% |
| SJC | US | 56.11% | 98.00% | 12 | 4 | 3.57% | 59.23% | 64.49% |
| NRT | JP | 55.68% | 92.94% | 12 | 5 | 3.57% | 58.13% | 64.34% |
| ICN | KR | 55.37% | 89.85% | 8 | 0 | 2.38% | 58.36% | 64.50% |

## Governance Interpretation

Edge PoPs with repeated high-utilization hours should be monitored during rollout. If quality improves but capacity risk increases, rollout decisions should consider both delivery quality and resource headroom.