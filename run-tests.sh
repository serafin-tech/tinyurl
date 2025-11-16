#!/usr/bin/env bash
set -euo pipefail

# Simple test runner for the repository.
# - Ensures a Python venv at backend/.venv
# - Installs backend in editable mode with dev extras (ruff, mypy, pytest, httpx, etc.) unless SKIP_INSTALL=1
# - Runs pytest using repository pytest.ini
# - Passes through any extra args to pytest

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_DIR="$BACKEND_DIR/.venv"

# Create venv if missing
if [[ ! -d "$VENV_DIR" ]]; then
  echo "[setup] Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# Activate venv
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# Upgrade pip
python -m pip install --upgrade pip >/dev/null

# Install project dependencies (editable with dev extras) unless skipped
if [[ "${SKIP_INSTALL:-0}" != "1" ]]; then
  echo "[setup] Installing backend dev dependencies"
  pip install -e "$BACKEND_DIR"[dev] >/dev/null
fi

# Ensure working directory is repo root so pytest.ini is picked up
cd "$ROOT_DIR"

# Run tests (pytest.ini sets testpaths and pythonpath)
echo "[test] Running pytest $*"
pytest "$@"
