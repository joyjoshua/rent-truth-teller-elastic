"""Canned demo queries for CLI dry-runs (requires data indexed and .env)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.agent import run_agent

QUERIES = [
    "Is ₹35,000 fair for a 2BHK semi-furnished in Koramangala?",
    "Broker wants 8 months deposit for a 1BHK in HSR at ₹22,000.",
    "Should I rent in Whitefield or Sarjapur if my budget is ₹25,000?",
]


def main() -> None:
    for q in QUERIES:
        print("=" * 60)
        print("Q:", q)
        print("-" * 60)
        print(run_agent(q))
        print()


if __name__ == "__main__":
    main()
