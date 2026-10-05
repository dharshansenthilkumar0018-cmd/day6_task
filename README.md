# Day 6 Task — Reliable Tool Calling

Scenario: **Campus Event Assistant**

## Files

- `tools.py` — two scenario-specific tools and strict schemas
- `validate.py` — schema validation
- `robust_agent.py` — reliable OpenAI-compatible agent loop
- `inject_faults.py` — 10 deterministic fault-injection cases
- `structured_demo.py` — free text, JSON mode and schema mode
- `analysis.md` — complete conceptual analysis and observation tables
- `screenshots/` — place required screenshots here
- `config.py` — provider/model setup
- `.env.example` — safe configuration template
- `.gitignore` — prevents `.env` and local environment files from being committed

## Setup

```bash
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure your provider.

## Run

```bash
python validate.py
python inject_faults.py
python robust_agent.py
python structured_demo.py
```

Run `inject_faults.py` first because it does not need a model or internet.

## GitHub submission

Commit the project but never commit `.env` or API keys. Add screenshots of:
1. validator output
2. fault injection output
3. each agent run, including a parallel-call run when supported
4. structured-output demo

Then push the repository and submit its GitHub link.
