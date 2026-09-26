#!/usr/bin/env sh
set -eu

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "ERROR: OPENAI_API_KEY is not set."
  echo "Set it in the n8n host environment or secret store; never commit the key."
  exit 2
fi

code="$(
  curl -sS -o /tmp/openai-healthcheck.json -w '%{http_code}' \
    https://api.openai.com/v1/models \
    -H "Authorization: Bearer ${OPENAI_API_KEY}"
)"

case "$code" in
  200)
    echo "OpenAI API authentication check: OK"
    ;;
  401)
    echo "OpenAI API authentication check: FAILED (401 Unauthorized)"
    exit 1
    ;;
  *)
    echo "OpenAI API check returned HTTP $code"
    cat /tmp/openai-healthcheck.json 2>/dev/null || true
    exit 1
    ;;
esac
