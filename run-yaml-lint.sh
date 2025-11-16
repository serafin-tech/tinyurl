#!/usr/bin/env bash
set -euo pipefail

# Run yamllint using project .yamllint config for docker-compose and any other YAML files.

if ! command -v yamllint >/dev/null 2>&1; then
  echo "[info] Installing yamllint (user)" >&2
  pip install --user yamllint >/dev/null
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$ROOT_DIR/.yamllint"
TARGETS=(docker-compose.yaml)

echo "[lint] yamllint using config $CONFIG_FILE"
yamllint -c "$CONFIG_FILE" "${TARGETS[@]}"
