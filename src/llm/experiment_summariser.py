from __future__ import annotations
import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def build_prompt(result: dict) -> str:
    return f"""
You are a data scientist writing an experiment readout for a video delivery quality experiment.

The experiment compares a control strategy and a treatment strategy for video delivery.

Experiment result:
{json.dumps(result, indent=2)}

Write a concise business-facing readout with:
1. Metric summary
2. Statistical interpretation
3. Guardrail interpretation
4. Recommendation

Important:
- Do not overclaim causality beyond the experiment.
- Mention that the treatment should be rolled out gradually.
- Keep it under 180 words.
"""


def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.2
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["response"]


def main():
    result = {
        "experiment_id": "protocol_test",
        "primary_metric": {
            "name": "latency_ms",
            "control": 33.8110,
            "treatment": 30.4250,
            "relative_lift": -0.100144,
            "p_value": 0.000001,
            "bootstrap_95_ci_difference_ms": [-3.4702, -3.3047],
        },
        "guardrail_metrics": {
            "startup_time_ms": {
                "control": 54.1048,
                "treatment": 48.6664,
                "direction": "improved",
            },
            "rebuffer_ratio": {
                "control": 0.0909,
                "treatment": 0.0818,
                "direction": "improved",
            },
        },
    }

    prompt = build_prompt(result)
    output = call_ollama(prompt)

    print("\n=== LLM Experiment Readout ===\n")
    print(output)


if __name__ == "__main__":
    main()