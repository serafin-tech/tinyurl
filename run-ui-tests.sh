#!/usr/bin/env bash
set -euo pipefail
# Runs Playwright e2e tests for the frontend UI.
# Requires the frontend to be running at http://localhost:5173 (docker compose up or npm run dev).

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
UI_DIR="$ROOT_DIR/frontend/ui"

cd "$UI_DIR"
echo "[e2e] Running Playwright tests in $UI_DIR"
npx playwright test "$@"
