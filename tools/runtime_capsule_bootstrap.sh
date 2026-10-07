#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -z "$DOMAIN" ]; then
  echo "Set DOMAIN to the public HTTPS hostname before running." >&2
  exit 2
fi
ENV_FILE="$ROOT/.env"
if [ -n "$RUNTIME_ENV_FILE" ]; then ENV_FILE="$RUNTIME_ENV_FILE"; fi

rand() { python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
}

if [[ -f "$ENV_FILE" ]]; then
  echo "Using existing deployment env: $ENV_FILE"
else
  umask 077
  cat > "$ENV_FILE" <<EOF
ACTION_GATE_ENV=production
DOMAIN=$DOMAIN
POSTGRES_PASSWORD=$(rand)
ACTION_GATE_API_TOKEN=$(rand)
ACTION_GATE_SIGNING_SECRET=$(rand)
ACTION_GATE_APPROVAL_SECRET=$(rand)
ACTION_GATE_AUTHORITY_SECRET=$(rand)
ACTION_GATE_STATE_ORACLE_SECRET=$(rand)
MCP_BEARER_TOKEN=$(rand)
EOF
  echo "Created deployment secrets in $ENV_FILE"
fi

docker compose -f action_gate/docker-compose.production.yml --env-file "$ENV_FILE" build
docker compose -f action_gate/docker-compose.production.yml --env-file "$ENV_FILE" up -d

echo "Waiting for Action Gate..."
for i in {1..30}; do
  if docker compose -f action_gate/docker-compose.production.yml --env-file "$ENV_FILE" exec -T action-gate python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/health").read()' >/dev/null 2>&1; then
    echo "Action Gate is healthy."
    break
  fi
  sleep 2
done

echo "Runtime capsule started."
docker compose -f action_gate/docker-compose.production.yml --env-file "$ENV_FILE" ps
