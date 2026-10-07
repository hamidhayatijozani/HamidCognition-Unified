#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE=".runtime.env"
COMPOSE_FILE="action_gate/docker-compose.production.yml"

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

failed=0
for service in postgres action-gate tool enforcement dashboard chatgpt-mcp; do
  state="$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps --status running --services | grep -Fx "$service" || true)"
  if [[ "$state" != "$service" ]]; then
    echo "UNHEALTHY: $service"
    failed=1
  else
    echo "RUNNING: $service"
  fi
done

python3 runtime/capsule.py

exit "$failed"
