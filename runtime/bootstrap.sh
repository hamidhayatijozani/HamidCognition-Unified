#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="action_gate/docker-compose.production.yml"
ENV_FILE=".runtime.env"

command -v docker >/dev/null 2>&1 || {
  echo "ERROR: Docker is required. Install Docker/Compose on the host first."
  exit 2
}
docker compose version >/dev/null 2>&1 || {
  echo "ERROR: Docker Compose v2 is required."
  exit 2
}

if [[ ! -f "$ENV_FILE" ]]; then
  umask 077
  random_secret() { python3 -c 'import secrets; print(secrets.token_urlsafe(48))'; }

  cat > "$ENV_FILE" <<EOF
POSTGRES_PASSWORD=$(random_secret)
ACTION_GATE_API_TOKEN=$(random_secret)
ACTION_GATE_SIGNING_SECRET=$(random_secret)
ACTION_GATE_APPROVAL_SECRET=$(random_secret)
ACTION_GATE_AUTHORITY_SECRET=$(random_secret)
MCP_BEARER_TOKEN=$(random_secret)
ACTION_GATE_KEY_ID=runtime-$(hostname -s)
DEMO_TENANT_ID=runtime-demo
DEMO_ACTOR_ID=runtime-host
DEMO_AGENT_ID=runtime-agent
DEMO_SESSION_ID=runtime-session
MCP_ISSUER_URL=https://invalid.local
MCP_RESOURCE_URL=https://localhost/mcp
MCP_REQUIRED_SCOPE=mcp:execute
MCP_CLIENT_ID=runtime-client
MCP_TOKEN_TTL_SECONDS=3600
DOMAIN=${DOMAIN:-localhost}
EOF
  echo "Created $ENV_FILE"
fi

if [[ -n "${DOMAIN:-}" ]]; then
  sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" "$ENV_FILE"
fi

echo "Building Action Gate runtime..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build

echo "Starting Action Gate runtime..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo "Waiting for services..."
sleep 5

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

echo "Generating runtime evidence capsule..."
python3 runtime/capsule.py

echo
echo "Runtime bootstrap complete."
echo "Evidence: evidence/runtime/runtime-capsule.json"
echo "Use: docker compose -f $COMPOSE_FILE --env-file $ENV_FILE ps"
