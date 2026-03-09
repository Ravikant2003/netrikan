# Netrikan Backend

## Overview
This is the FastAPI backend for the Netrikan project. It provides APIs for route safety, risk assessment, emergency handling, and user/guardian management.

## Setup
1. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints
- `/health` — Health check
- `/api/analyze` — Analyze location/context
- `/api/route` — Get best route
- `/api/risk` — Assess risk
- `/api/emergency` — Emergency trigger
- `/api/register` — Register user
- `/api/login` — Login for demo token
- `/api/me` — Current session user
- `/api/logout` — Invalidate session token
- `/api/guardian` — Add guardian

## Security
- Use `POST /api/login` with demo credentials from env (`DEMO_USERNAME` / `DEMO_PASSWORD`).
- Pass returned token in header `X-Auth-Token` for protected endpoints: `/api/analyze`, `/api/risk`, `/api/route`, `/api/emergency`, `/api/me`, `/api/logout`.
- `POST /api/register` and `POST /api/guardian` are open for easier project demo flow.
- Basic in-memory rate limiting is enabled per client IP (env: `RATE_LIMIT_PER_MINUTE`, default `120`).

## Testing
Run backend tests with:
```bash
python validate_backend.py
python -m pytest -q tests/test_agents.py
```

## Notes
- User and guardian data is stored in SQLite (`backend/data/netrikan.db`).
- See `agent_manager.py` and `routes/` for logic.
