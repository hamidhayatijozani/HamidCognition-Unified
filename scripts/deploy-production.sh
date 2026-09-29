#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/hamidcognition}"
REPO="${REPO:-https://github.com/hamidhayatijozani/HamidCognition-Unified.git}"
DOMAIN="${DOMAIN:?DOMAIN is required}"

mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO" "$APP_DIR"
else
  git -C "$APP_DIR" fetch origin main
  git -C "$APP_DIR" checkout main
  git -C "$APP_DIR" reset --hard origin/main
fi

cd "$APP_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required on the deployment host" >&2
  exit 20
fi
docker compose version >/dev/null 2>&1 || {
  echo "docker compose plugin is required on the deployment host" >&2
  exit 21
}

ENV_FILE="$APP_DIR/action_gate/.env.production"
if [ ! -f "$ENV_FILE" ]; then
  umask 077
  cat > "$ENV_FILE" <<EOF
ACTION_GATE_ENV=production
ACTION_GATE_API_TOKEN=$(openssl rand -hex 32)
ACTION_GATE_SIGNING_SECRET=$(openssl rand -hex 48)
ACTION_GATE_AUTHORITY_SECRET=$(openssl rand -hex 48)
ACTION_GATE_APPROVAL_SECRET=$(openssl rand -hex 48)
ACTION_GATE_KEY_ID=hhj-action-gate-1
ACTION_GATE_REQUIRE_SESSION_BINDING=1
ACTION_GATE_RATE_LIMIT_PER_MINUTE=120
ACTION_GATE_DECISION_TTL_SECONDS=300
ACTION_GATE_APPROVAL_TTL_SECONDS=300
POSTGRES_DB=action_gate
POSTGRES_USER=action_gate
POSTGRES_PASSWORD=$(openssl rand -hex 32)
DOMAIN=$DOMAIN
MCP_BEARER_TOKEN=$(openssl rand -hex 32)
EOF
  chmod 600 "$ENV_FILE"
else
  sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" "$ENV_FILE"
fi

docker compose --env-file "$ENV_FILE" -f action_gate/docker-compose.production.yml config --quiet
docker compose --env-file "$ENV_FILE" -f action_gate/docker-compose.production.yml up -d --build

for i in $(seq 1 60); do
  if docker compose --env-file "$ENV_FILE" -f action_gate/docker-compose.production.yml ps --status running | grep -q action-gate; then
    if curl -fsS --max-time 3 "https://$DOMAIN/health" >/dev/null 2>&1; then
      echo "deployment healthy: https://$DOMAIN"
      exit 0
    fi
  fi
  sleep 5
done

docker compose --env-file "$ENV_FILE" -f action_gate/docker-compose.production.yml ps
exit 30
