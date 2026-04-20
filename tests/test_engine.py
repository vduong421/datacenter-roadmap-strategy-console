import unittest
from pathlib import Path

from src.datacenter_roadmap_strategy_console.engine import load_json, prioritize_roadmap


class EngineTests(unittest.TestCase):
    def test_prioritize_roadmap_returns_ranked_initiatives(self) -> None:
        base = Path(__file__).resolve().parents[1] / "samples"
        customers = load_json(base / "customers.json")
        technologies = load_json(base / "technologies.json")
        competitors = load_json(base / "competitors.json")

        result = prioritize_roadmap(customers, technologies, competitors)

        self.assertIsNotNone(result["top_priority"])
        self.assertEqual(len(result["initiatives"]), 3)
        self.assertGreaterEqual(
            result["initiatives"][0]["priority_score"],
            result["initiatives"][1]["priority_score"],
        )


if __name__ == "__main__":
    unittest.main()
