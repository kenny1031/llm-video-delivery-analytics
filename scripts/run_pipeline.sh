#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo " Video Delivery Analytics Pipeline"
echo "========================================"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "ERROR: .venv not found. Please create and activate a Python virtual environment first."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "ERROR: .env file not found."
  exit 1
fi

set -a
source .env
set +a

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set in .env"
  exit 1
fi

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-55434}"
DB_USER="${DB_USER:-delivery}"
DB_NAME="${DB_NAME:-video_delivery_analytics}"

echo ""
echo "Step 1/10: Checking Docker containers..."
docker compose up -d

echo ""
echo "Step 2/10: Checking required processed YouTube data..."
if [ ! -f "data/processed/youtube_videos.parquet" ]; then
  echo "ERROR: data/processed/youtube_videos.parquet not found."
  echo "Run: python src/data/ingest_youtube_api.py"
  exit 1
fi

echo ""
echo "Step 3/10: Generating synthetic delivery logs..."
python src/data/generate_delivery_logs.py

echo ""
echo "Step 4/10: Generating edge capacity snapshots..."
python src/data/generate_capacity_snapshots.py

echo ""
echo "Step 5/10: Applying database schema..."
PGPASSWORD="${DB_PASSWORD:-delivery}" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f sql/schema.sql

echo ""
echo "Step 6/10: Resetting database tables..."
PGPASSWORD="${DB_PASSWORD:-delivery}" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -c "TRUNCATE TABLE delivery_events, videos, edge_capacity_snapshots RESTART IDENTITY;"

echo ""
echo "Step 7/10: Loading parquet files into Postgres..."
python src/data/load_to_postgres.py

echo ""
echo "Step 8/10: Running SQL metric checks..."
mkdir -p reports/sql_outputs

PGPASSWORD="${DB_PASSWORD:-delivery}" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f sql/metrics/quality_metrics.sql \
  > reports/sql_outputs/quality_metrics.txt

PGPASSWORD="${DB_PASSWORD:-delivery}" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f sql/metrics/cost_metrics.sql \
  > reports/sql_outputs/cost_metrics.txt

PGPASSWORD="${DB_PASSWORD:-delivery}" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f sql/metrics/capacity_metrics.sql \
  > reports/sql_outputs/capacity_metrics.txt

PGPASSWORD="${DB_PASSWORD:-delivery}" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f sql/metrics/network_segment_metrics.sql \
  > reports/sql_outputs/network_segment_metrics.txt

echo ""
echo "Step 9/10: Running Python analytics reports..."
python src/experiments/ab_test_latency.py | tee reports/experiment_readout_raw.txt
python src/metrics/cost_quality_report.py
python src/metrics/capacity_report.py
python src/metrics/root_cause_diagnostics.py
python src/metrics/rule_based_root_cause.py

echo ""
echo "Step 10/10: Running local LLM summaries if Ollama is available..."

if curl -s "${OLLAMA_BASE_URL:-http://localhost:11434}/api/tags" > /dev/null; then
  python src/llm/experiment_summariser.py | tee reports/llm_outputs/protocol_test_readout.md
  python src/llm/root_cause_assistant.py
else
  echo "WARNING: Ollama is not running. Skipping LLM summaries."
  echo "Start Ollama with: ollama serve"
fi

echo ""
echo "========================================"
echo " Pipeline completed successfully"
echo "========================================"
echo "Generated reports:"
echo "- reports/cost_quality_report.md"
echo "- reports/capacity_report.md"
echo "- reports/diagnostics/rule_based_root_cause.md"
echo "- reports/llm_outputs/protocol_test_readout.md"
echo "- reports/llm_outputs/root_cause_hypotheses.md"