# TinyURL Monorepo (MVP)

This repository hosts a TinyURL-style application with a FastAPI backend, MongoDB persistence, a Svelte management UI, and an Nginx gateway that fronts the public redirect surface, the authenticated management UI, and the authenticated API surface.

## Contents
- `backend/` – FastAPI application source and its own README with feature details.
- `docs/` – Requirements and design notes.

## Prerequisites
- Python 3.11+
- Docker (optional but recommended for Compose)
- Git

## Environment Setup (Local Python)

1) Create a virtual environment
```bash
python -m venv backend/.venv
```

2) Activate the environment
Linux/macOS:
```bash
. backend/.venv/bin/activate
```
Windows (PowerShell):
```powershell
backend\.venv\Scripts\Activate.ps1
```

3) Upgrade pip (recommended)
```bash
python -m pip install --upgrade pip
```

4) Install dependencies (editable + dev)
```bash
pip install -e backend/[dev]
```

## Running the Stack

Option A: Docker Compose
```bash
BASIC_AUTH_USER=admin BASIC_AUTH_PASSWORD=change-me docker compose up --build
```
Open:

- `http://localhost:8000/<link-id>` for public redirects
- `http://localhost:8000/mgnt/` for the management UI (basic auth)
- `http://localhost:8000/api/docs` for backend API docs (basic auth)

Option B: Local Python
```bash
uvicorn src.api.app:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

- BASE_URL (default: http://localhost:8000)
- MONGODB_URI (default: mongodb://localhost:27017)
- MONGODB_DB (default: tinyurl)
- TOKEN_PEPPER (default: devpepper)
- BASIC_AUTH_USER / BASIC_AUTH_PASSWORD (used by the Nginx gateway in Compose)

Local example:
```bash
export BASE_URL=http://localhost:8000
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DB=tinyurl
export TOKEN_PEPPER=devpepper
uvicorn src.api.app:app --app-dir backend --reload
```

## Testing & Tooling

- Run backend tests: `bash run-tests.sh`
- Lint: `ruff check backend/src`
- Format check: `ruff format --check backend/src`
- Type check: `mypy backend/src`

(Optional) Pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Roadmap

1. Domain model & validation (in progress)
2. Persistence & repository (SQLite)
3. Use cases (create/update/delete/resolve)
4. HTTP API endpoints
5. Redirect endpoint
6. Rate limiting
7. Tests (unit & integration)
8. Observability basics (logging, request IDs)
9. Frontend stub (optional)
10. Redis-backed redirect cache
11. Abuse controls (domain blocklist)
