.PHONY: install db-up pipeline dashboard test clean

install:
	pip install -r requirements.txt

db-up:
	docker compose up -d

pipeline:
	./scripts/run_pipeline.sh

dashboard:
	./scripts/run_dashboard.sh

test:
	pytest

clean:
	rm -rf reports/sql_outputs
	rm -rf reports/diagnostics/*_diagnostics.csv
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +