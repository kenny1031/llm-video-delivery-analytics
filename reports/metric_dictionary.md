# Metric Dictionary

This document defines the core metrics used in the **LLM-assisted Video Delivery Quality & Cost Analytics Platform**.

The goal is to support video delivery quality governance, CDN cost monitoring, resource capacity analysis, and experiment decision-making.

---

## 1. Delivery Quality Metrics

### 1.1 Average Latency

**Definition**

Average network delivery latency per video delivery event.

```text
avg_latency_ms = AVG(latency_ms)
```

**Interpretation**

Lower latency generally indicates faster content delivery and better playback responsiveness.

**Usage**

- Primary metric for delivery quality experiments
- Segment analysis by region, edge PoP, protocol, and IP version
- Guardrail for rollout decisions

---

### 1.2 Startup Time

**Definition**

Average time between playback request and video start.

```text
avg_startup_time_ms = AVG(startup_time_ms)
```

**Interpretation**

Lower startup time means users can start watching videos faster.

**Usage**

- Guardrail metric for quality experiments
- Used to ensure latency improvements also translate into user-facing playback improvement

---

### 1.3 Rebuffer Ratio

**Definition**

Average fraction of playback time affected by buffering.

```text
avg_rebuffer_ratio = AVG(rebuffer_ratio)
```

**Interpretation**

Lower rebuffer ratio indicates smoother video playback.

**Usage**

- Key video quality guardrail
- Used to detect whether a delivery strategy improves latency but harms playback stability

---

### 1.4 Quality-adjusted Delivery Score

**Definition**

A composite delivery quality score combining latency, startup time, and rebuffering.

Example formulation:

```text
quality_score =
    - w1 * normalized_latency
    - w2 * normalized_startup_time
    - w3 * normalized_rebuffer_ratio
```

**Interpretation**

Higher score indicates better overall delivery quality.

**Usage**

- Optional ranking metric for comparing regions, edge PoPs, or delivery strategies
- Useful when multiple quality metrics move in different directions

---

## 2. Cost Governance Metrics

### 2.1 Total CDN Cost

**Definition**

Total estimated CDN cost across delivery events.

```text
total_cdn_cost_usd = SUM(cdn_cost_usd)
```

**Interpretation**

Measures total delivery cost for a traffic segment or experiment group.

**Usage**

- Business bill monitoring
- Regional and edge PoP cost decomposition
- Guardrail for rollout decisions

---

### 2.2 Average Cost per Event

**Definition**

Average CDN cost per delivery event.

```text
avg_cost_per_event = AVG(cdn_cost_usd)
```

**Interpretation**

Measures unit cost of serving a video delivery event.

**Usage**

- Comparing cost efficiency across variants, regions, or edge PoPs
- Monitoring cost drift during rollout

---

### 2.3 Cost per 1K Events

**Definition**

CDN cost normalized per 1,000 delivery events.

```text
cost_per_1k_events =
    SUM(cdn_cost_usd) / COUNT(*) * 1000
```

**Interpretation**

A normalized business cost metric that makes segments with different traffic volumes comparable.

**Usage**

- Primary cost governance metric
- Used in cost-quality tradeoff analysis
- Useful for comparing regions and edge PoPs

---

### 2.4 Cache Hit Rate

**Definition**

Fraction of delivery events served from cache.

```text
cache_hit_rate = AVG(cache_hit)
```

where `cache_hit` is 1 if the event was served from cache and 0 otherwise.

**Interpretation**

Higher cache hit rate usually indicates better CDN efficiency and potentially lower origin retrieval cost.

**Usage**

- Cost guardrail metric
- Helps determine whether cost or latency changes may be associated with cache efficiency
- Monitored by region and edge PoP

---

## 3. Capacity and Resource Utilization Metrics

### 3.1 Edge Utilization Ratio

**Definition**

Fraction of edge PoP capacity currently used.

```text
utilization_ratio =
    used_capacity_mbps / max_capacity_mbps
```

**Interpretation**

Higher utilization indicates less available capacity headroom.

**Usage**

- Capacity planning
- Detecting overloaded edge PoPs
- Rollout guardrail for traffic increases

---

### 3.2 Peak Utilization

**Definition**

Maximum observed utilization for an edge PoP over a time window.

```text
peak_utilization = MAX(utilization_ratio)
```

**Interpretation**

Captures worst-case capacity pressure.

**Usage**

- Identifying edge PoPs that may require capacity expansion
- Monitoring risk during large traffic spikes

---

### 3.3 High-utilization Hours

**Definition**

Number of hourly snapshots where utilization exceeds a warning threshold.

```text
high_utilization_hours =
    COUNT(snapshot_time WHERE utilization_ratio >= 0.85)
```

**Interpretation**

Measures how often an edge PoP operates under high load.

**Usage**

- Capacity risk monitoring
- Identifying persistent rather than one-off capacity pressure

---

### 3.4 Critical-utilization Hours

**Definition**

Number of hourly snapshots where utilization exceeds a critical threshold.

```text
critical_utilization_hours =
    COUNT(snapshot_time WHERE utilization_ratio >= 0.90)
```

**Interpretation**

Measures severe capacity pressure.

**Usage**

- Escalation signal for capacity planning
- Rollout guardrail for new delivery strategies

---

### 3.5 High-utilization Share

**Definition**

Share of snapshots where utilization exceeds the high-utilization threshold.

```text
high_utilization_share =
    high_utilization_hours / total_hours
```

**Interpretation**

Normalizes high-utilization frequency across different time windows.

**Usage**

- Comparing edge PoP capacity risk
- Ranking capacity planning priorities

---

### 3.6 CPU Utilization

**Definition**

Average simulated CPU utilization for an edge PoP.

```text
avg_cpu_utilization = AVG(cpu_utilization)
```

**Interpretation**

Measures compute resource pressure.

**Usage**

- Resource capacity analysis
- Guardrail for rollout decisions

---

### 3.7 Memory Utilization

**Definition**

Average simulated memory utilization for an edge PoP.

```text
avg_memory_utilization = AVG(memory_utilization)
```

**Interpretation**

Measures memory resource pressure.

**Usage**

- Resource capacity analysis
- Detecting potential memory bottlenecks

---

## 4. Experiment Metrics

### 4.1 Absolute Difference

**Definition**

Difference between treatment and control metric values.

```text
absolute_difference =
    treatment_metric - control_metric
```

**Interpretation**

For latency, startup time, rebuffer ratio, and cost, negative values usually indicate improvement.

**Usage**

- A/B test readout
- Segment-level diagnostics

---

### 4.2 Relative Lift

**Definition**

Relative change from control to treatment.

```text
relative_lift =
    (treatment_metric - control_metric) / control_metric
```

**Interpretation**

Shows percentage improvement or degradation compared with the control group.

**Usage**

- Experiment summary
- Comparing effects across metrics with different units

---

### 4.3 Bootstrap Confidence Interval

**Definition**

A non-parametric confidence interval estimated by repeatedly resampling control and treatment groups.

```text
bootstrap_diff =
    mean(treatment_resample) - mean(control_resample)
```

The 95% confidence interval is computed using the 2.5th and 97.5th percentiles of bootstrap differences.

**Interpretation**

If the confidence interval for a difference does not include zero, the treatment effect is unlikely to be random noise.

**Usage**

- A/B test uncertainty estimation
- Robust reporting for experiment readouts

---

### 4.4 P-value

**Definition**

Probability of observing an effect at least as extreme as the measured effect under the null hypothesis.

**Interpretation**

A small p-value suggests the observed difference is unlikely under the null hypothesis.

**Usage**

- Statistical significance check
- Experiment decision support

**Caution**

The p-value should not be interpreted as the probability that the treatment is correct or that the effect is practically important.

---

## 5. Segment Dimensions

### 5.1 Region

Examples:

```text
AU, US, SG, JP, KR
```

Used to compare delivery quality, cost, and capacity across user geographies.

---

### 5.2 Edge PoP

Examples:

```text
SYD, MEL, SIN, NRT, ICN, LAX, SJC
```

Used to analyze CDN edge performance and capacity risk.

---

### 5.3 Protocol

Examples:

```text
TCP, QUIC, HTTP3
```

Used to compare delivery behavior across network/application transport protocols.

---

### 5.4 IP Version

Examples:

```text
IPv4, IPv6
```

Used to compare delivery quality and cost across IP versions.

---

## 6. Decision Framework

Experiment decisions should consider three groups of metrics.

### 6.1 Primary Quality Metric

Example:

```text
avg_latency_ms
```

The main metric the treatment is expected to improve.

---

### 6.2 Quality Guardrails

Examples:

```text
startup_time_ms
rebuffer_ratio
```

These ensure the treatment does not improve one metric while harming user-facing playback quality.

---

### 6.3 Business and Capacity Guardrails

Examples:

```text
cost_per_1k_events
cache_hit_rate
high_utilization_share
critical_utilization_hours
```

These ensure rollout decisions do not create unacceptable cost or resource capacity risk.

---

## 7. LLM Usage Policy

The LLM is not the source of truth for metric decisions.

The LLM may be used for:

1. Rewriting statistical outputs into business-facing experiment readouts.
2. Summarizing SQL/Python diagnostics.
3. Generating cautious root-cause hypotheses.
4. Supporting knowledge Q&A over metric definitions and governance notes.

The LLM must not invent unmeasured causes such as packet loss, routing changes, cache misses, CPU bottlenecks, or origin-server latency unless those signals are explicitly measured in the data.

Final decisions rely on:

```text
SQL metrics
statistical tests
bootstrap confidence intervals
deterministic diagnostics
```
