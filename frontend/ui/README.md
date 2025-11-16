# TinyURL UI (Svelte + Vite)

A minimal UI to interact with the TinyURL FastAPI backend.

## Features
- Create short links (optional custom alias, choose redirect code)
- Update target URL, redirect code, or change alias (requires edit token)
- Delete (soft) a link (requires edit token)
- Simple redirect tester (shows status and Location header)

## Prerequisites
- Backend running locally (default): http://localhost:8000
- Option A: Docker (recommended) — no local Node install required
- Option B: Local Node.js 18+ if you prefer running without Docker

## Quick start (Docker, recommended)
From the repository root:

```
# dev server (http://localhost:5173), auto-installs deps inside container
./run-ui-docker.sh dev

# build & preview production bundle (http://localhost:5174)
./run-ui-docker.sh preview

# build only (dist output in frontend/ui/dist)
./run-ui-docker.sh build

# clean node_modules volume used by the container
./run-ui-docker.sh clean
```

Environment variables:
- VITE_API_BASE: Backend API base URL (default http://localhost:8000)

Examples:
```
VITE_API_BASE=http://127.0.0.1:8000 ./run-ui-docker.sh dev
```

## Running locally with Node
If you’d rather run with a local Node runtime:

```
cd frontend/ui
npm install
npm run dev
```
Visit http://localhost:5173

Optionally create `.env`:
```
VITE_API_BASE=http://localhost:8000
```

## CORS
The backend enables CORS and by default allows http://localhost:5173.
Override allowed origins on the backend with:

```
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Notes
- The UI reads `VITE_API_BASE` at build/runtime for API calls.
- Ensure your backend is reachable from the browser (network and CORS).
- Redirect tester performs a manual fetch to `/{link_id}` and reports status & Location.

## Troubleshooting
- If the Docker dev server can’t bind the port, ensure 5173 is free or set `PORT_DEV` when running the script:
  - `PORT_DEV=5175 ./run-ui-docker.sh dev`
- If you see CORS errors, verify the backend `ALLOW_ORIGINS` includes your UI origin.