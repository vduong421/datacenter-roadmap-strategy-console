# Datacenter Roadmap Strategy Console

A strategy-planning and execution-visibility engine for translating customer requirements, validation readiness, dashboard health, and competitive pressure into a prioritized storage roadmap.

## Why It Matches The Role

- Builds dashboard-style visibility for initiative health, validation coverage, and execution readiness
- Adds AI-assisted recommendations for reporting and test-triage workflows
- Shows how customer signals can be turned into roadmap and execution priorities for a global storage team

## Features

- Customer-segment requirement scoring
- Standards readiness and competitive pressure modeling
- Initiative prioritization for roadmap planning
- Validation and dashboard visibility scoring
- AI-assisted program brief and initiative recommendations
- Executive-friendly JSON summary output

## Run

```powershell
python -m src.datacenter_roadmap_strategy_console.cli --customers samples\customers.json --technologies samples\technologies.json --competitors samples\competitors.json
```

## Web Dashboard

```powershell
python server.py
```

Then open `http://127.0.0.1:8003`.
