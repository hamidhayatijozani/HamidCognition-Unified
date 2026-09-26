# n8n + OpenAI deployment

## 1. Prepare the secret

Create an OpenAI API key in the OpenAI platform and keep it in the n8n host environment or a secret manager.

Do not paste a real key into Git, workflow JSON, README files, shell history, or issue comments.

For local Docker Compose usage:

    cp .env.example .env

Then set:

    OPENAI_API_KEY=YOUR_REAL_KEY

The repository ignores `.env`.

## 2. Start n8n

From the repository root:

    cd n8n
    docker compose up -d

n8n will be available on port 5678 unless the host configuration is changed.

## 3. Verify the credential

With the same environment loaded:

    OPENAI_API_KEY="$OPENAI_API_KEY" ./scripts/openai-healthcheck.sh

A successful check prints:

    OpenAI API authentication check: OK

## 4. Configure the n8n credential

Inside n8n, create an OpenAI credential and provide the API key through n8n's credential mechanism.

Prefer n8n's encrypted credential storage over embedding the key in workflow nodes.

## Security invariant

This repository intentionally contains only configuration templates and executable checks. It must never contain the real value of `OPENAI_API_KEY`.
