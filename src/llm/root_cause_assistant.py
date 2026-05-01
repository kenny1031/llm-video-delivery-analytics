from __future__ import annotations

import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

INPUT_PATH = Path("reports/diagnostics/rule_based_root_cause.md")
OUTPUT_PATH = Path("reports/llm_outputs/root_cause_hypotheses.md")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def build_prompt(rule_summary: str) -> str:
    return f"""
Rewrite the following rule-based data science summary into a concise business-facing root-cause hypothesis report.

Critical instructions:
- Do not add any new facts, metrics, causes, or technical explanations.
- Do not mention packet loss, CPU utilization, cache misses, routing, congestion, buffer size, packet size, or origin servers.
- Preserve all numeric values exactly as given.
- Keep the conclusion cautious: these are hypotheses and monitoring notes, not proven root causes.
- Keep it under 200 words.

Rule-based summary:
{rule_summary}
"""


def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.0,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["response"]


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_PATH}. Run src/metrics/rule_based_root_cause.py first."
        )

    rule_summary = INPUT_PATH.read_text(encoding="utf-8")
    output = call_ollama(build_prompt(rule_summary))

    OUTPUT_PATH.write_text(output, encoding="utf-8")

    print("\n=== LLM Root Cause Hypotheses ===\n")
    print(output)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()