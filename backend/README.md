# TinyURL Backend MVP

FastAPI-based URL shortener backend using MongoDB. The backend now sits behind an Nginx gateway that serves the authenticated management UI under `/api/` and forwards public redirect traffic from the root path.

- Tech: FastAPI, MongoDB, Motor, Pydantic v2
- Deployment: Docker Compose with Nginx gateway + backend + MongoDB
- Security: Edit token (24-char), hashed (sha256 + optional pepper)
- Redirects: 301/302/307/308; 410 for deleted; 404 for not found

## Quickstart

You can run the backend via Docker Compose (recommended) or locally with Python.

### Option A: Docker Compose
```bash
BASIC_AUTH_USER=admin BASIC_AUTH_PASSWORD=change-me docker compose up --build
```
Open:

- `http://localhost:8000/api/` for the management UI (basic auth)
- `http://localhost:8000/api/docs` for API docs (basic auth)
- `http://localhost:8000/<link-id>` for public redirects

### Option B: Local Python
From the repository root:
```bash
python -m venv backend/.venv
. backend/.venv/bin/activate
python -m pip install --upgrade pip
pip install -e backend/[dev]

uvicorn src.api.app:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```
Open http://localhost:8000/api/docs.

## Configuration

Environment variables (Docker Compose provides defaults):

- MONGODB_URI: MongoDB connection string (default: mongodb://localhost:27017)
- MONGODB_DB: Database name (default: tinyurl)
- BASE_URL: Base URL used when returning shortened links (default: http://localhost:8000)
- TOKEN_PEPPER: Pepper used before hashing edit tokens (default: devpepper)

Local example:
```bash
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DB=tinyurl
export BASE_URL=http://localhost:8000
export TOKEN_PEPPER=devpepper
uvicorn src.api.app:app --app-dir backend --reload
```

## API Overview

OpenAPI docs:

- Local backend directly: `http://localhost:8000/api/docs`
- Through Compose gateway: `http://localhost:8000/api/docs`

- GET `/api/health` → `{ "status": "ok" }`
- POST `/api/links` – create a short link; auto-generated IDs retry collisions up to 5 times before failing with 500
- PATCH `/api/links/{link_id}` – update (requires `X-Edit-Token`)
- DELETE `/api/links/{link_id}` – delete (requires `X-Edit-Token`)
- GET/HEAD `/{link_id}` – backend redirect endpoint (when exposed through Nginx, public root traffic is limited to GET)

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
- Port 8000 busy → change the published gateway port in `docker-compose.yaml`
- MongoDB connection errors → verify `MONGODB_URI` and that the `mongodb` service is healthy
