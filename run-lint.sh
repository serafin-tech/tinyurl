#!/usr/bin/env bash
set -euo pipefail

# Lint/typecheck runner for the repository.
# - Ensures backend/.venv
# - Installs backend with dev extras unless SKIP_INSTALL=1
# - Runs Ruff (lint) and Mypy (package-mode) against src

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

cd "$BACKEND_DIR"

# Ruff lint
echo "[lint] Ruff check"
ruff check --quiet

# Mypy type check (package mode)
echo "[type] Mypy check (src.* packages)"
mypy --hide-error-codes --hide-error-context -p src.api -p src.adapters -p src.domain

# Optional: format check (uncomment to enforce)
# echo "[fmt] Ruff format --check"
# ruff format --check

echo "[ok] Lint & type checks passed"
