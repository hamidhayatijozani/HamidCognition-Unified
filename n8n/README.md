# n8n + OpenAI

This directory contains the non-secret deployment and credential templates for connecting n8n to OpenAI.

## Files

- `.env.example`: safe environment template.
- `docker-compose.yml`: production-oriented n8n container configuration.
- `scripts/openai-healthcheck.sh`: checks whether `OPENAI_API_KEY` authenticates successfully.
- `SETUP.md`: deployment and credential setup procedure.

## Environment

Copy `.env.example` to `.env` on the n8n host and set `OPENAI_API_KEY`, or configure the value through a secret manager / n8n credential mechanism.

Never commit `.env` or a real API key. The repository `.gitignore` excludes `.env` files while allowing `.env.example`.

## Required variable

`OPENAI_API_KEY` = the OpenAI API key generated for this n8n deployment.

Security invariant: this repository contains no real API credential.
