# Netrikan_02

Netrikan is a safety navigation platform with:
- FastAPI backend (`/backend`)
- Agentic orchestration (tools + planner + memory)
- Flutter frontend (`/mobile_app`) with web build support

## Run with Docker (recommended for teammates)

This mode needs only Docker Desktop (no Python/Flutter setup).

### 1) Start everything

```zsh
docker compose up --build -d
```

### 2) Open in browser

- Frontend UI: `http://localhost:8080`
- Backend API docs: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/health`

### 3) Stop

```zsh
docker compose down
```

## Rebuild after code changes

```zsh
docker compose up --build -d
```

## Useful checks

```zsh
docker compose ps
docker compose logs -f backend
docker compose logs -f web
```

## Notes

- Web build is generated in the web container using Flutter.
- Frontend uses `API_BASE_URL=http://localhost:8000` for browser access.
- If ports are occupied, stop conflicting services first.
