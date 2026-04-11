#!/usr/bin/env bash
set -euo pipefail

# Run Renovate locally inside Docker against the checked-in renovate.json.
# This uses Renovate's experimental local platform in dry-run mode by default,
# which is useful for validating config and seeing proposed updates.
#
# Usage:
#   ./run-renovate-local.sh
#   ./run-renovate-local.sh --dry-run=full
#   LOG_LEVEL=debug ./run-renovate-local.sh
#
# Env overrides:
#   DOCKER_IMAGE=renovate/renovate:latest
#   LOG_LEVEL=info
#   RENOVATE_DRY_RUN=lookup
#   RENOVATE_GITHUB_COM_TOKEN=<token>   # optional, helps avoid GitHub API rate limits

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/renovate.json"
DOCKER_IMAGE="${DOCKER_IMAGE:-renovate/renovate:latest}"
LOG_LEVEL="${LOG_LEVEL:-info}"
RENOVATE_DRY_RUN="${RENOVATE_DRY_RUN:-lookup}"
CACHE_DIR="$SCRIPT_DIR/.renovate/cache"
HOST_UID="${HOST_UID:-$(id -u)}"
HOST_GID="${HOST_GID:-$(id -g)}"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "[err] Renovate config not found at $CONFIG_FILE" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[err] Docker is required to run Renovate locally." >&2
  exit 1
fi

mkdir -p "$CACHE_DIR"

DOCKER_RUN=(docker run --rm)
if [[ -t 0 && -t 1 ]]; then
  DOCKER_RUN+=(-it)
fi

DOCKER_RUN+=(
  -v "$SCRIPT_DIR:/work"
  -v "$CACHE_DIR:/tmp/renovate"
  -u "$HOST_UID:$HOST_GID"
  -w /work
  -e "LOG_LEVEL=$LOG_LEVEL"
  -e "RENOVATE_PLATFORM=local"
  -e "RENOVATE_DRY_RUN=$RENOVATE_DRY_RUN"
)

if [[ -n "${RENOVATE_GITHUB_COM_TOKEN:-}" ]]; then
  DOCKER_RUN+=(-e "RENOVATE_GITHUB_COM_TOKEN=$RENOVATE_GITHUB_COM_TOKEN")
fi

echo "[info] Pulling Docker image: $DOCKER_IMAGE"
docker pull "$DOCKER_IMAGE" >/dev/null

echo "[info] Running Renovate locally from /work"
echo "[info] Local mode is experimental and does not create branches."
"${DOCKER_RUN[@]}" "$DOCKER_IMAGE" --platform=local "$@"
