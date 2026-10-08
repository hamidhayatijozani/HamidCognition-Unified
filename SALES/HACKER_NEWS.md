# Hacker News draft

## Title

Show HN: Action Gate, a pre-execution authorization boundary for AI-agent tools

## Post

I built Action Gate to address a narrow problem: an AI agent may be able to call a privileged tool, but the tool still needs an independently verifiable authorization boundary.

The flow is:

Agent → Action Gate → Protected Tool

Action Gate evaluates the requested action, binds the decision to tenant/actor/session/action context, issues execution authority, and enforces the governed path. It supports HTTP and MCP enforcement, replay protection, fail-closed evidence handling, PostgreSQL persistence, and audit/replay evidence.

The current commercial release is v1.1.1. It is proprietary, not open source.

The repository is public for provenance, technical inspection, and reproducibility. Public visibility does not grant a license to reproduce, modify, redistribute, or commercialize the proprietary product.

A practical proof-of-value is deliberately small: protect one high-impact tool or MCP server, run the acceptance suite, and inspect the resulting evidence.

Repository:
https://github.com/hamidhayatijozani/HamidCognition-Unified

Commercial release:
https://github.com/hamidhayatijozani/HamidCognition-Unified/releases/tag/action-gate-v1.1.1
