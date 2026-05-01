# LLM-assisted Video Delivery Quality & Cost Analytics Platform

This project simulates a TikTok-style data analytics platform for video delivery quality, CDN cost governance, and edge resource capacity analysis.

It combines:
- YouTube Data API ingestion for real video metadata
- Synthetic CDN delivery event generation
- PostgreSQL-based quality, cost, and capacity metrics
- A/B testing with bootstrap confidence intervals
- Local Ollama LLM experiment readout generation
- Grounded root-cause hypothesis generation based on SQL/Python diagnostics

The LLM is not used as the source of truth for decisions. SQL metrics, statistical tests, and deterministic diagnostics remain the source of truth. The LLM is used only to rewrite structured analysis into business-facing summaries.

```text
YouTube Data API
        ↓
video metadata parquet
        ↓
synthetic CDN delivery logs
        ↓
PostgreSQL
        ↓
SQL metrics
        ├── quality governance
        ├── cost governance
        └── capacity governance
        ↓
Python analysis
        ├── A/B testing
        ├── bootstrap CI
        ├── cost-quality report
        └── capacity report
        ↓
Local LLM assistant
        ├── experiment readout
        └── grounded root-cause hypothesis report
```

## Running the Pipeline

The full local analytics pipeline can be executed with:

```bash
chmod +x scripts/run_pipeline.sh
./scripts/run_pipeline.sh
```
