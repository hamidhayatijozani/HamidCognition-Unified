# n8n OpenAI credential setup

This directory contains the non-secret configuration template for connecting n8n to OpenAI.

## Environment

Copy `.env.example` to `.env` on the n8n host and set `OPENAI_API_KEY` there, or configure the value through the n8n credential/environment mechanism.

Never commit `.env` or a real API key. The repository `.gitignore` excludes `.env` files while allowing `.env.example`.

## Required variable

`OPENAI_API_KEY` = the OpenAI API key generated for this n8n deployment.
