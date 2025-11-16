#!/usr/bin/env bash
set -euo pipefail

# Run yamllint using project .yamllint config for docker-compose and any other YAML files.

if ! command -v yamllint >/dev/null 2>&1; then
  echo "[info] Installing yamllint (user)" >&2
  pip install --user yamllint >/dev/null
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$ROOT_DIR/.yamllint"
# Use args or find all YAML files, excluding node_modules and .git
if [ $# -gt 0 ]; then
  TARGETS=("$@")
else
  mapfile -t TARGETS < <(find "$ROOT_DIR" -type f \( -name "*.yaml" -o -name "*.yml" \) ! -path "*/node_modules/*" ! -path "*/.git/*")
fi

echo "[lint] yamllint using config $CONFIG_FILE"
yamllint -c "$CONFIG_FILE" "${TARGETS[@]}"
