from __future__ import annotations

import argparse
import json

from .engine import load_json, prioritize_roadmap


def main() -> None:
    parser = argparse.ArgumentParser(description="Prioritize datacenter storage roadmap initiatives.")
    parser.add_argument("--customers", required=True, help="Path to customer JSON.")
    parser.add_argument("--technologies", required=True, help="Path to technology JSON.")
    parser.add_argument("--competitors", required=True, help="Path to competitor JSON.")
    args = parser.parse_args()

    customers = load_json(args.customers)
    technologies = load_json(args.technologies)
    competitors = load_json(args.competitors)
    result = prioritize_roadmap(customers, technologies, competitors)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

