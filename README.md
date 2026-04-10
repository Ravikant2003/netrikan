# Netrikan_02

Netrikan is a safety navigation platform with:
- FastAPI backend (`/backend`)
- Agentic orchestration (LangGraph + tools + multi-agent reasoning)
- Flutter frontend (`/mobile_app`) with web build support

## Development Setup

The project is running locally using a direct Python/FastAPI backend and Flutter/Web frontend.

### 1) Start Backend
Run the backend server using the provided startup script (it uses `uv` for speed if installed):
```zsh
./start_backend.sh
```

## Useful checks
- Backend health: `http://localhost:8000/health`
- Backend API docs: `http://localhost:8000/docs`

## Tools
- **uv**: The project is optimized to use `uv` for lightning-fast dependency management.

## Notes
- The project follows a **3-Layer Agentic Architecture** (Monitoring, Decision Agents, and Action Execution).
- For details, see the backend core modules.

## Agentic AI (Backend)
The agentic workflow is implemented in:
- `backend/core/orchestrator.py` (LangGraph: Layer1 → Layer2 → Layer3)
- `backend/core/layer2_agents.py` (agentic reasoning; Gemini-only)
- `backend/core/policy.py` (safety guardrails for actions/tools)

### Configure Gemini
Layer 2 runs in Gemini-only mode (no rule-based fallback). Configure `GEMINI_API_KEY` in `backend/.env`.

### Safety simulation (demo)
Backend exposes a simulation endpoint that returns a per-step trace including the policy audit:
- `POST /api/simulate` with `{"scenario_id":"prompt_injection" | "sos" | "route_risk" | "normal"}`
- `GET /api/simulate/scenarios` to list built-in scenarios

Recommended demo env (no routing network calls):
```zsh
export NETRIKAN_NO_NETWORK=1
```
