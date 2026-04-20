# Datacenter Roadmap Strategy Console

A strategy-planning engine for translating customer requirements, standards timing, and competitive pressure into a prioritized storage roadmap.

## Why It Matches The Role

- Aligns customer engagement with technology planning
- Helps drive quarterly technology reviews
- Balances ecosystem signals, product differentiation, and future architecture bets

## Features

- Customer-segment requirement scoring
- Standards readiness and competitive pressure modeling
- Initiative prioritization for roadmap planning
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
