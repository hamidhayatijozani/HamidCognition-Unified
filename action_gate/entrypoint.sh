#!/bin/sh
set -eu
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-action_gate}"
POSTGRES_DB="${POSTGRES_DB:-action_gate}"
echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Postgres not ready, waiting..."
  sleep 2
done
echo "Postgres ready. Starting app..."
exec "$@"
