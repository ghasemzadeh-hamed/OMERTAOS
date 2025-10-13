# AgentOS FastAPI Control Plane

This service orchestrates inference requests between local Rust modules and remote LLM providers. The bundled heuristic decision router illustrates how latency budgets, task intent, and prompt size influence routing choices.

## Running locally

```bash
cd core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
