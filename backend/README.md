# TinyURL Backend MVP

FastAPI-based minimal URL shortener backend using SQLite. This MVP supports creating, updating, deleting, and resolving short links as described in the project requirements (no Redis, no Kubernetes).

- Tech: FastAPI, SQLite, SQLAlchemy, Pydantic v2
- Deployment: Docker Compose (single service)
- Security: Edit token (24-char), hashed (sha256 + optional pepper)
- Redirects: 301/302/307/308; 410 for deleted; 404 for not found

## Quickstart

You can run the backend via Docker Compose (recommended) or locally with Python.

### Option A: Docker Compose
```bash
docker compose up --build
```
Open http://localhost:8000/docs to view the API docs.

The SQLite database file is stored in a Docker volume at `/data/links.db`.

### Option B: Local Python
From the repository root:
```bash
python -m venv backend/.venv
. backend/.venv/bin/activate
python -m pip install --upgrade pip
pip install -e backend/[dev]

uvicorn src.api.app:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```
Open http://localhost:8000/docs.

## Configuration

Environment variables (Docker Compose provides defaults):

- SQLITE_DB_PATH: Path to SQLite file (default: /data/links.db)
- BASE_URL: Base URL used when returning shortened links (default: http://localhost:8000)
- TOKEN_PEPPER: Pepper used before hashing edit tokens (default: devpepper)
- RATE_LIMIT_CREATE / RATE_LIMIT_UPDATE / RATE_LIMIT_DELETE: per-IP per minute (default: 100)

Local example:
```bash
export SQLITE_DB_PATH=./backend/data/links.db
export BASE_URL=http://localhost:8000
export TOKEN_PEPPER=devpepper
export RATE_LIMIT_CREATE=100
export RATE_LIMIT_UPDATE=100
export RATE_LIMIT_DELETE=100
uvicorn src.api.app:app --app-dir backend --reload
```

## API Overview

OpenAPI docs: http://localhost:8000/docs

- GET `/api/health` → `{ "status": "ok" }`
- POST `/api/links` – create a short link
- PATCH `/api/links/{link_id}` – update (requires `X-Edit-Token`)
- DELETE `/api/links/{link_id}` – delete (requires `X-Edit-Token`)
- GET/HEAD `/{link_id}` – redirect (404 if missing, 410 if deleted)

Example create request:
```bash
curl -sS -X POST http://localhost:8000/api/links \
  -H 'Content-Type: application/json' \
  -d '{"target_url":"https://example.com","redirect_code":301}'
```

## Development

- Ruff lint: `ruff check backend/src`
- Format check: `ruff format --check backend/src`
- Type check: `mypy backend/src`
- Tests (to be added later): `pytest -q`

## Troubleshooting

- VS Code unresolved imports → ensure interpreter is `backend/.venv/bin/python`
- Port 8000 busy → use `--port 8001`
- SQLite write errors → set writable `SQLITE_DB_PATH`