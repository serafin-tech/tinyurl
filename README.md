# TinyURL Monorepo (MVP)

This repository hosts the TinyURL MVP implementation. Current scope: a backend service (FastAPI + SQLite) with a minimal redirect and CRUD API. Future stages will add frontend and expanded features.

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

## Running the Backend

Option A: Docker Compose
```bash
cd backend
docker compose up --build
```
Open http://localhost:8000/docs

Option B: Local Python
```bash
uvicorn src.api.app:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

- SQLITE_DB_PATH (default: /data/links.db)
- BASE_URL (default: http://localhost:8000)
- TOKEN_PEPPER (default: devpepper)
- RATE_LIMIT_CREATE / RATE_LIMIT_UPDATE / RATE_LIMIT_DELETE (default: 100)

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

## Testing & Tooling

- Run tests: `pytest -q` (once tests are added)
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
10. Static assets / robots.txt
11. Abuse controls (domain blocklist)