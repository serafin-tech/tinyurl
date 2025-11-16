#!/usr/bin/env bash
set -euo pipefail

# Run the TinyURL Svelte UI inside a Docker container using the latest Node LTS image.
# No local Node installation required.
#
# Usage:
#   ./run-ui-docker.sh [dev|preview|build|clean]
#
# Env overrides:
#   DOCKER_IMAGE=node:lts-alpine   # change Node image
#   VITE_API_BASE=http://localhost:8000  # backend API base
#   PORT_DEV=5173                  # vite dev port
#   PORT_PREVIEW=5174              # vite preview port

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_DIR="$SCRIPT_DIR/frontend/ui"

if [[ ! -d "$UI_DIR" ]]; then
  echo "[err] UI directory not found at $UI_DIR" >&2
  exit 1
fi

DOCKER_IMAGE="${DOCKER_IMAGE:-node:lts-alpine}"
CMD="${1:-dev}"
PORT_DEV="${PORT_DEV:-5173}"
PORT_PREVIEW="${PORT_PREVIEW:-5174}"
VITE_API_BASE="${VITE_API_BASE:-http://localhost:8000}"
VOLUME_NAME="tinyurl_ui_node_modules"

echo "[info] Pulling Docker image: $DOCKER_IMAGE"
docker pull "$DOCKER_IMAGE" >/dev/null

# Base docker run args
DOCKER_RUN=(
  docker run --rm -it
  -u "$(id -u):$(id -g)"
  -v "$UI_DIR:/app"
  -v "$VOLUME_NAME:/app/node_modules"
  -w /app
  -e "VITE_API_BASE=$VITE_API_BASE"
)

case "$CMD" in
  dev)
    echo "[info] Starting Vite dev server on port $PORT_DEV (API: $VITE_API_BASE)"
    "${DOCKER_RUN[@]}" -p "$PORT_DEV:$PORT_DEV" "$DOCKER_IMAGE" \
      sh -lc "npm install && npm run dev -- --host 0.0.0.0 --port $PORT_DEV"
    ;;

  preview)
    echo "[info] Building UI and serving preview on port $PORT_PREVIEW (API: $VITE_API_BASE)"
    "${DOCKER_RUN[@]}" -p "$PORT_PREVIEW:$PORT_PREVIEW" "$DOCKER_IMAGE" \
      sh -lc "npm install && npm run build && npm run preview -- --host 0.0.0.0 --port $PORT_PREVIEW"
    ;;

  build)
    echo "[info] Building production UI (API: $VITE_API_BASE)"
    "${DOCKER_RUN[@]}" "$DOCKER_IMAGE" \
      sh -lc "npm install && npm run build"
    ;;

  clean)
    echo "[info] Removing node_modules volume: $VOLUME_NAME"
    docker volume rm "$VOLUME_NAME" || true
    ;;

  *)
    echo "Usage: $0 [dev|preview|build|clean]" >&2
    exit 2
    ;;
esac
