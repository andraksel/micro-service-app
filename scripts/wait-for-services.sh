#!/usr/bin/env sh
set -eu

BASE_URL="${GATEWAY_URL:-http://localhost:8080}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-90}"
STARTED_AT="$(date +%s)"

while true; do
  if curl -fsS "$BASE_URL/ready" >/dev/null; then
    echo "Gateway is ready: $BASE_URL"
    exit 0
  fi

  NOW="$(date +%s)"
  if [ "$((NOW - STARTED_AT))" -ge "$TIMEOUT_SECONDS" ]; then
    echo "Timed out waiting for $BASE_URL" >&2
    exit 1
  fi

  sleep 2
done
