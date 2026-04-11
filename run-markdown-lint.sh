#!/usr/bin/env bash
set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "[error] npx is required to run markdownlint-cli2. Install Node.js/npm first." >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$ROOT_DIR/.markdownlint.jsonc"

if [ $# -gt 0 ]; then
  TARGETS=("$@")
else
  TARGETS=(
    "$ROOT_DIR/**/*.md"
    "#$ROOT_DIR/**/node_modules/**"
    "#$ROOT_DIR/**/dist/**"
    "#$ROOT_DIR/**/.git/**"
    "#$ROOT_DIR/**/.venv/**"
    "#$ROOT_DIR/**/.renovate/**"
    "#$ROOT_DIR/**/test-results/**"
  )
fi

echo "[lint] markdownlint-cli2 using config $CONFIG_FILE"
npx --yes markdownlint-cli2 --config "$CONFIG_FILE" "${TARGETS[@]}"
