from __future__ import annotations

import json
from pathlib import Path


def load_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def prioritize_roadmap(customers: list[dict], technologies: list[dict], competitors: list[dict]) -> dict:
    competitor_map = {item["name"]: set(item["focus_areas"]) for item in competitors}
    initiatives = []

    for technology in technologies:
        demand_score = 0.0
        for customer in customers:
            segment_score = 0.0
            for metric, weight in customer["priorities"].items():
                segment_score += weight * technology["customer_value"][metric]
            demand_score += customer["weight"] * segment_score

        competitor_pressure = sum(
            0.12 for focus_areas in competitor_map.values() if technology["name"] in focus_areas
        )

        priority_score = (
            demand_score * 0.50
            + technology["standards_readiness"] * 0.20
            + technology["competitive_gap"] * 0.25
            - technology["execution_risk"] * 0.15
            + competitor_pressure
        )

        initiatives.append(
            {
                "name": technology["name"],
                "demand_score": round(demand_score, 3),
                "standards_readiness": technology["standards_readiness"],
                "execution_risk": technology["execution_risk"],
                "competitive_gap": technology["competitive_gap"],
                "competitor_pressure": round(competitor_pressure, 3),
                "priority_score": round(priority_score, 3),
                "action": _build_action(priority_score, technology["standards_readiness"]),
            }
        )

    ranked = sorted(initiatives, key=lambda item: item["priority_score"], reverse=True)
    return {
        "top_priority": ranked[0]["name"] if ranked else None,
        "initiatives": ranked,
        "quarterly_review_message": _quarterly_review_message(ranked[:2]),
    }


def _build_action(priority_score: float, readiness: float) -> str:
    if priority_score > 0.72 and readiness >= 0.60:
        return "Escalate to roadmap commit and customer co-validation."
    if priority_score > 0.60:
        return "Advance prototyping and standards engagement."
    return "Monitor signal quality and refine business case."


def _quarterly_review_message(top_items: list[dict]) -> str:
    if not top_items:
        return "No initiatives available."
    joined = "; ".join(f"{item['name']} ({item['priority_score']})" for item in top_items)
    return f"Recommended quarterly review emphasis: {joined}."

