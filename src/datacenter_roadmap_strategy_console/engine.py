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
        validation_score = round(
            technology["validation_coverage"] * 0.55 + technology["test_automation"] * 0.45,
            3,
        )
        visibility_score = round(
            technology["dashboard_readiness"] * 0.60 + technology["repo_health"] * 0.40,
            3,
        )
        ai_leverage = round(
            technology["ai_assist_opportunity"] * 0.55 + visibility_score * 0.25 + validation_score * 0.20,
            3,
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
                "validation_score": validation_score,
                "visibility_score": visibility_score,
                "ai_leverage": ai_leverage,
                "action": _build_action(priority_score, technology["standards_readiness"]),
                "ai_recommendation": _build_ai_recommendation(
                    technology["name"],
                    validation_score,
                    visibility_score,
                    ai_leverage,
                ),
            }
        )

    ranked = sorted(initiatives, key=lambda item: item["priority_score"], reverse=True)
    coverage_gap = max((1.0 - item["validation_score"] for item in ranked), default=0.0)
    weakest_visibility = min((item["visibility_score"] for item in ranked), default=0.0)
    return {
        "top_priority": ranked[0]["name"] if ranked else None,
        "initiatives": ranked,
        "quarterly_review_message": _quarterly_review_message(ranked[:2]),
        "portfolio_health": {
            "average_validation_score": round(
                sum(item["validation_score"] for item in ranked) / max(len(ranked), 1),
                3,
            ),
            "average_visibility_score": round(
                sum(item["visibility_score"] for item in ranked) / max(len(ranked), 1),
                3,
            ),
            "largest_coverage_gap": round(coverage_gap, 3),
            "weakest_visibility_signal": round(weakest_visibility, 3),
        },
        "ai_program_brief": _build_program_brief(ranked),
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


def _build_ai_recommendation(
    name: str,
    validation_score: float,
    visibility_score: float,
    ai_leverage: float,
) -> str:
    if validation_score < 0.62:
        return f"Use an AI triage assistant on {name} to cluster validation escapes and expand regression coverage."
    if visibility_score < 0.65:
        return f"Use an AI reporting workflow on {name} to summarize dashboard drift, stale tests, and repo health issues."
    if ai_leverage > 0.72:
        return f"Use {name} as the pilot for AI-generated review notes and execution-status summaries."
    return f"Keep {name} in the AI pipeline for weekly status digests and anomaly explanations."


def _build_program_brief(ranked: list[dict]) -> str:
    if not ranked:
        return "No roadmap signals available."
    top = ranked[0]
    if top["validation_score"] < 0.65:
        return (
            f"Highest-priority initiative is {top['name']}, but validation depth trails demand. "
            "Increase automated coverage before broader roadmap commitment."
        )
    if top["visibility_score"] < 0.65:
        return (
            f"{top['name']} leads on demand and strategy, but dashboard and repository visibility need work "
            "before scaling execution across teams."
        )
    return (
        f"{top['name']} is the best candidate for a combined roadmap, dashboard, and AI-assisted execution pilot."
    )
