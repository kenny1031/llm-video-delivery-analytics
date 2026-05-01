# LLM-assisted Video Delivery Quality & Cost Analytics Platform

A local data analytics project for video delivery quality, CDN cost governance, and edge resource capacity monitoring.

The project combines API-based video metadata ingestion, synthetic CDN delivery logs, PostgreSQL metrics, A/B testing, cost and capacity reports, and local LLM-assisted readouts. The LLM is used only to rewrite structured analysis into business-facing summaries; SQL metrics, statistical tests, and deterministic diagnostics remain the source of truth.

---

## Project Overview

Modern video platforms need to balance delivery quality, infrastructure cost, and edge capacity. This project simulates that workflow with a small but end-to-end analytics system.

The system answers questions such as:

- Did the treatment delivery strategy reduce latency?
- Did startup time and rebuffer ratio improve as guardrail metrics?
- Did the improvement increase CDN cost?
- Which regions or edge PoPs contributed most to the change?
- Are any edge PoPs approaching capacity risk?
- Can a local LLM generate a readable experiment readout without inventing unsupported causes?

---

## Core Features

- **YouTube API ingestion** for real video metadata.
- **Synthetic CDN delivery log generation** for latency, startup time, rebuffer ratio, cache hit, cost, protocol, IP version, region, and edge PoP signals.
- **PostgreSQL metrics layer** for quality, cost, capacity, and segment diagnostics.
- **A/B testing framework** with relative lift, Welch two-sample t-test, and bootstrap confidence intervals.
- **Cost governance report** covering cost per 1K events, cache hit rate, and cost-quality tradeoffs.
- **Capacity monitoring** using simulated edge PoP capacity snapshots, CPU utilization, memory utilization, and high-utilization thresholds.
- **Grounded root-cause workflow** using deterministic SQL/Python diagnostics first, followed by local LLM rewriting.
- **Local Ollama LLM integration** for experiment readouts and hypothesis summarisation.
- **Streamlit dashboard** for interactive exploration of quality, cost, capacity, and LLM readouts.
- **Bash pipeline automation** for reproducible local execution.

---

## Architecture

```text
YouTube Data API
        |
        v
Raw JSON / Processed Parquet
        |
        v
Synthetic CDN Delivery Logs
        |
        v
PostgreSQL
        |
        +-----------------------------+
        |                             |
        v                             v
SQL Metrics                    Python Analytics
        |                             |
        |                             +--> A/B testing
        |                             +--> Bootstrap CI
        |                             +--> Cost-quality report
        |                             +--> Capacity report
        |                             +--> Rule-based diagnostics
        |
        v
Streamlit Dashboard
        |
        v
Local Ollama LLM
        |
        +--> Experiment readout rewriting
        +--> Grounded root-cause summary rewriting
```

---

## Repository Structure

```text
llm-video-delivery-analytics/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic_delivery/
│   └── llm_enriched/
│
├── sql/
│   ├── schema.sql
│   └── metrics/
│       ├── quality_metrics.sql
│       ├── cost_metrics.sql
│       ├── capacity_metrics.sql
│       └── network_segment_metrics.sql
│
├── src/
│   ├── data/
│   │   ├── ingest_youtube_api.py
│   │   ├── generate_delivery_logs.py
│   │   ├── generate_capacity_snapshots.py
│   │   └── load_to_postgres.py
│   │
│   ├── experiments/
│   │   └── ab_test_latency.py
│   │
│   ├── metrics/
│   │   ├── cost_quality_report.py
│   │   ├── capacity_report.py
│   │   ├── root_cause_diagnostics.py
│   │   └── rule_based_root_cause.py
│   │
│   ├── llm/
│   │   ├── experiment_summariser.py
│   │   └── root_cause_assistant.py
│   │
│   └── dashboard/
│       └── app.py
│
├── reports/
│   ├── metric_dictionary.md
│   ├── experiment_readout.md
│   ├── cost_quality_report.md
│   ├── capacity_report.md
│   ├── diagnostics/
│   └── llm_outputs/
│
├── scripts/
│   ├── run_pipeline.sh
│   └── run_dashboard.sh
│
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Data Sources

### Real metadata

Video metadata is collected through the YouTube Data API. The ingestion script fetches popular videos by region and stores both raw JSON responses and processed Parquet/CSV files.

Example fields:

- `video_id`
- `channel_id`
- `channel_title`
- `title`
- `description`
- `tags`
- `category_id`
- `published_at`
- `view_count`
- `like_count`
- `comment_count`

### Synthetic delivery logs

Public datasets usually do not contain internal CDN delivery logs, so this project generates synthetic delivery events based on the collected video metadata.

Example fields:

- `region_code`
- `edge_pop`
- `protocol`
- `ip_version`
- `latency_ms`
- `startup_time_ms`
- `rebuffer_ratio`
- `bitrate_kbps`
- `cache_hit`
- `cdn_cost_usd`
- `experiment_id`
- `variant`

### Synthetic capacity snapshots

The project also simulates hourly edge capacity snapshots for resource capacity analysis.

Example fields:

- `snapshot_time`
- `edge_pop`
- `region_code`
- `max_capacity_mbps`
- `used_capacity_mbps`
- `utilization_ratio`
- `active_connections`
- `cpu_utilization`
- `memory_utilization`

---

## Metric System

The project defines metrics across four groups.

### Delivery quality

- Average latency
- Startup time
- Rebuffer ratio
- Cache hit rate

### Cost governance

- Total CDN cost
- Average cost per event
- Cost per 1K events
- Cost-quality tradeoff by region and edge PoP

### Capacity governance

- Average utilization
- Peak utilization
- High-utilization hours
- Critical-utilization hours
- High-utilization share
- CPU utilization
- Memory utilization

### Experiment analysis

- Absolute treatment-control difference
- Relative lift
- Welch two-sample t-test
- Bootstrap confidence interval
- Guardrail metric checks

Detailed definitions are available in [`reports/metric_dictionary.md`](reports/metric_dictionary.md).

---

## Example Experiment Result

The project simulates a delivery strategy experiment with `control` and `treatment` variants.

Example result:

```text
Control mean latency:   33.81 ms
Treatment mean latency: 30.42 ms
Relative lift:         -10.01%
Bootstrap 95% CI:      [-3.47 ms, -3.30 ms]
P-value:               < 0.001
```

Interpretation:

The treatment reduces average delivery latency by approximately 10%, and the result is statistically significant. Startup time and rebuffer ratio also improve, while CDN cost remains a guardrail metric during rollout.

---

## LLM Usage Policy

The LLM is not used as the source of truth for analytical decisions.

The project uses a local Ollama model for:

1. Rewriting statistical experiment outputs into business-facing readouts.
2. Rewriting deterministic root-cause summaries into concise hypothesis reports.
3. Making technical reports easier to read.

The LLM must not invent causes that are not measured in the data, such as packet loss, routing changes, cache misses, CPU bottlenecks, or origin-server latency.

Final decisions are grounded in:

```text
SQL metrics
statistical tests
bootstrap confidence intervals
rule-based diagnostics
```

The root-cause workflow is intentionally designed as:

```text
SQL/Python diagnostics
        ↓
rule-based source-of-truth summary
        ↓
local LLM rewrite
```

This avoids LLM-dependent decision making.

---

## Dashboard

The Streamlit dashboard includes five pages:

1. **Overview** — high-level quality, cost, and capacity summary.
2. **Quality Experiment** — control vs treatment metrics and segment diagnostics.
3. **Cost Governance** — cost per 1K events and cost breakdowns.
4. **Capacity Risk** — edge PoP utilization and capacity risk monitoring.
5. **LLM Readouts** — experiment readout, root-cause hypothesis summary, and metric dictionary.

![Dashboard overview](docs/images/dashboard_overview.png)

```text
docs/images/dashboard_overview.png
```

Then include it with:

```md
![Dashboard overview](docs/images/dashboard_overview.png)
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/llm-video-delivery-analytics.git
cd llm-video-delivery-analytics
```

### 2. Create Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Fill in the required values:

```env
DATABASE_URL=postgresql+psycopg2://delivery:delivery@localhost:55434/video_delivery_analytics

DB_HOST=localhost
DB_PORT=55434
DB_USER=delivery
DB_PASSWORD=delivery
DB_NAME=video_delivery_analytics

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_GENERATE_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2:3b

YOUTUBE_API_KEY=your_youtube_api_key_here

PROJECT_NAME=llm-video-delivery-analytics
ENV=local
```

Do not commit `.env`.

### 4. Start Postgres

```bash
docker compose up -d
```

Or:

```bash
make db-up
```

### 5. Ingest YouTube metadata

```bash
python src/data/ingest_youtube_api.py
```

This creates:

```text
data/raw/youtube/*.json
data/processed/youtube_videos.csv
data/processed/youtube_videos.parquet
```

### 6. Run the full pipeline

```bash
./scripts/run_pipeline.sh
```

Or:

```bash
make pipeline
```

The pipeline runs synthetic data generation, schema setup, database loading, SQL metrics, Python reports, and optional local LLM readouts.

### 7. Launch dashboard

```bash
./scripts/run_dashboard.sh
```

Or:

```bash
make dashboard
```

Then open:

```text
http://localhost:8501
```

---

## Pipeline Steps

The automated Bash pipeline performs:

1. Docker/Postgres startup
2. Required data checks
3. Synthetic CDN delivery log generation
4. Edge capacity snapshot generation
5. Database schema setup
6. Database reset and Parquet-to-Postgres loading
7. SQL metric execution
8. A/B test analysis
9. Cost-quality report generation
10. Capacity report generation
11. Root-cause diagnostics
12. Rule-based root-cause summary generation
13. Optional local Ollama LLM readout generation

---

## Generated Reports

Key generated outputs include:

```text
reports/experiment_readout.md
reports/cost_quality_report.md
reports/capacity_report.md
reports/diagnostics/rule_based_root_cause.md
reports/llm_outputs/protocol_test_readout.md
reports/llm_outputs/root_cause_hypotheses.md
reports/metric_dictionary.md
```

---

## Example Commands

Run quality metrics:

```bash
psql -h localhost -p 55434 -U delivery -d video_delivery_analytics -f sql/metrics/quality_metrics.sql
```

Run A/B test:

```bash
python src/experiments/ab_test_latency.py
```

Run cost report:

```bash
python src/metrics/cost_quality_report.py
```

Run capacity report:

```bash
python src/metrics/capacity_report.py
```

Run root-cause workflow:

```bash
python src/metrics/root_cause_diagnostics.py
python src/metrics/rule_based_root_cause.py
python src/llm/root_cause_assistant.py
```

Run dashboard:

```bash
streamlit run src/dashboard/app.py
```

---

## Makefile Commands

```bash
make install      # install dependencies
make db-up        # start Postgres
make pipeline     # run full local analytics pipeline
make dashboard    # launch Streamlit dashboard
make test         # run tests
make clean        # remove generated intermediate outputs
```

---

## Notes on Synthetic Data

The CDN delivery and capacity data are synthetic by design. They are used to simulate a realistic analytics workflow where internal delivery logs are not publicly available.

The project focuses on:

- metric design
- data pipeline structure
- SQL analytics
- statistical decision-making
- cost and capacity governance
- safe LLM-assisted reporting

The synthetic data should not be interpreted as real network performance data.

---

## Tech Stack

- Python
- pandas / NumPy / SciPy
- PostgreSQL
- SQLAlchemy
- Docker Compose
- Streamlit
- Plotly
- Bash scripting
- Ollama local LLM
- YouTube Data API

---

## Status

Current project status:

- API ingestion: complete
- Synthetic delivery log generation: complete
- PostgreSQL schema and loading: complete
- Quality metrics and A/B testing: complete
- Cost governance report: complete
- Capacity report: complete
- Grounded root-cause workflow: complete
- Local LLM readouts: complete
- Streamlit dashboard: complete
- Pipeline automation: complete