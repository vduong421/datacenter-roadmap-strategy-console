from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.datacenter_roadmap_strategy_console.engine import load_json, prioritize_roadmap


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
SHARED = ROOT.parent / "_shared_project_workbench"

if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

try:
    from local_llm import chat_json
except Exception:
    chat_json = None


def load_inputs() -> tuple[list[dict], list[dict], list[dict]]:
    customers = load_json(ROOT / "samples" / "customers.json")
    technologies = load_json(ROOT / "samples" / "technologies.json")
    competitors = load_json(ROOT / "samples" / "competitors.json")
    return customers, technologies, competitors


def build_result() -> dict:
    customers, technologies, competitors = load_inputs()
    result = prioritize_roadmap(customers, technologies, competitors)
    initiatives = result.get("initiatives", [])

    high_risk = sorted(initiatives, key=lambda item: item["execution_risk"], reverse=True)[:3]
    strongest_demand = sorted(initiatives, key=lambda item: item["demand_score"], reverse=True)[:3]
    strongest_gap = sorted(initiatives, key=lambda item: item["competitive_gap"], reverse=True)[:3]

    result["deterministic_reasoning"] = {
        "high_risk_initiatives": high_risk,
        "strongest_demand_initiatives": strongest_demand,
        "largest_competitive_gaps": strongest_gap,
        "initiative_count": len(initiatives),
        "customer_segment_count": len(customers),
        "competitor_count": len(competitors),
    }
    return result


roadmap_result = build_result()


def fallback_ai_insights() -> dict:
    reasoning = roadmap_result["deterministic_reasoning"]
    top = roadmap_result["initiatives"][0] if roadmap_result["initiatives"] else {}
    risk_names = [item["name"] for item in reasoning["high_risk_initiatives"]]

    return {
        "result": f"Top roadmap priority is {roadmap_result.get('top_priority')} with priority score {top.get('priority_score')}.",
        "recommendation": "Commit the top initiative to customer co-validation while tracking high-risk initiatives separately.",
        "decision": "Proceed with roadmap review using the ranked initiatives and risk notes.",
        "executive_summary": f"{reasoning['initiative_count']} initiatives were scored across {reasoning['customer_segment_count']} customer segments and {reasoning['competitor_count']} competitors.",
        "top_risks": [
            f"Highest execution-risk initiatives: {', '.join(risk_names)}.",
            "Competitive gaps may require faster roadmap commitment.",
            "Low-readiness initiatives should stay in prototype or standards engagement."
        ],
        "operator_actions": [
            "Review top priority with customer-facing roadmap stakeholders.",
            "Assign mitigation owners for the highest execution-risk initiatives.",
            "Use competitive gap scores to prepare quarterly review talking points."
        ],
        "resume_signal": "Built a datacenter roadmap strategy console with deterministic scoring and local-AI grounded planning guidance."
    }


def generate_ai_insights(model: str = "google/gemma-4-e4b") -> dict:
    if chat_json is None:
        return fallback_ai_insights()

    prompt = f"""You are a senior datacenter roadmap strategy analyst.

Return ONLY valid JSON with:
- result
- recommendation
- decision
- executive_summary
- top_risks array of 3
- operator_actions array of 3
- resume_signal

Rules:
- use only deterministic roadmap output
- no hallucinated metrics
- be concise and executive-friendly

Roadmap output:
{json.dumps(roadmap_result, indent=2)}
"""
    try:
        ai = chat_json(prompt, model=model)
        if not isinstance(ai, dict):
            return fallback_ai_insights()
        return {
            "result": ai.get("result", ""),
            "recommendation": ai.get("recommendation", ""),
            "decision": ai.get("decision", ""),
            "executive_summary": ai.get("executive_summary", ""),
            "top_risks": ai.get("top_risks", []),
            "operator_actions": ai.get("operator_actions", []),
            "resume_signal": ai.get("resume_signal", "")
        }
    except Exception:
        return fallback_ai_insights()


ai_copilot = generate_ai_insights()


def answer_question(question: str, model: str = "google/gemma-4-e4b") -> dict:
    q = question.lower()
    reasoning = roadmap_result["deterministic_reasoning"]

    fallback = {
        "answer": f"Top priority is {roadmap_result.get('top_priority')}.",
        "evidence": roadmap_result.get("quarterly_review_message", ""),
        "next_action": "Review the top initiative and compare it against risk and readiness.",
        "recommendation": ai_copilot["recommendation"],
        "decision": ai_copilot["decision"],
        "risks": ai_copilot["top_risks"],
        "operator_actions": ai_copilot["operator_actions"],
    }

    if "risk" in q:
        items = reasoning["high_risk_initiatives"]
        fallback["answer"] = "Highest execution-risk initiatives: " + ", ".join(item["name"] for item in items) + "."
        fallback["evidence"] = "; ".join(f"{item['name']} risk={item['execution_risk']}" for item in items)
        fallback["next_action"] = "Assign mitigation plans before roadmap commitment."
    elif "demand" in q or "customer" in q:
        items = reasoning["strongest_demand_initiatives"]
        fallback["answer"] = "Strongest demand initiatives: " + ", ".join(item["name"] for item in items) + "."
        fallback["evidence"] = "; ".join(f"{item['name']} demand={item['demand_score']}" for item in items)
        fallback["next_action"] = "Use demand scores to prepare customer validation sessions."
    elif "competitive" in q or "gap" in q:
        items = reasoning["largest_competitive_gaps"]
        fallback["answer"] = "Largest competitive gaps: " + ", ".join(item["name"] for item in items) + "."
        fallback["evidence"] = "; ".join(f"{item['name']} gap={item['competitive_gap']}" for item in items)
        fallback["next_action"] = "Review competitive positioning and differentiation urgency."
    elif "top" in q or "priority" in q:
        top = roadmap_result["initiatives"][0]
        fallback["answer"] = f"{top['name']} is ranked first with score {top['priority_score']}."
        fallback["evidence"] = f"Demand={top['demand_score']}, readiness={top['standards_readiness']}, gap={top['competitive_gap']}, risk={top['execution_risk']}."
        fallback["next_action"] = top["action"]

    if chat_json is None:
        return fallback

    prompt = f"""You are a datacenter roadmap copilot.

Answer using ONLY deterministic roadmap output.

Return ONLY valid JSON with:
- answer
- evidence
- next_action
- recommendation
- decision
- risks array
- operator_actions array

Question:
{question}

Roadmap output:
{json.dumps(roadmap_result, indent=2)}

AI analyst:
{json.dumps(ai_copilot, indent=2)}
"""
    try:
        response = chat_json(prompt, model=model)
        if not isinstance(response, dict):
            return fallback
        return {
            "answer": response.get("answer", fallback["answer"]),
            "evidence": response.get("evidence", fallback["evidence"]),
            "next_action": response.get("next_action", fallback["next_action"]),
            "recommendation": response.get("recommendation", fallback["recommendation"]),
            "decision": response.get("decision", fallback["decision"]),
            "risks": response.get("risks", fallback["risks"]),
            "operator_actions": response.get("operator_actions", fallback["operator_actions"]),
        }
    except Exception:
        return fallback


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/run":
            self._send_json({
                **roadmap_result,
                "ai_copilot": ai_copilot,
            })
            return

        target = "index.html" if self.path in ("/", "") else self.path.lstrip("/")
        file_path = WEB_ROOT / target
        if file_path.exists() and file_path.is_file():
            self._send_file(file_path)
            return
        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        if self.path == "/api/ask":
            length = int(self.headers.get("Content-Length", 0))
            question = self.rfile.read(length).decode("utf-8")
            self._send_json(answer_question(question))
            return
        self.send_error(404, "Not Found")

    def log_message(self, format: str, *args) -> None:
        return

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }.get(path.suffix, "application/octet-stream")
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8003), Handler)
    print("Roadmap strategy dashboard running at http://127.0.0.1:8003")
    server.serve_forever()


if __name__ == "__main__":
    main()

