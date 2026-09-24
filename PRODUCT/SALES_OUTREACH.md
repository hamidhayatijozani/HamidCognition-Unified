# HamidCognition Action Gate — Sales Outreach Package

## Objective

Start enterprise conversations around the Action Gate execution-governance boundary without disclosing implementation-sensitive material before NDA.

## Primary buyer roles

- Head of AI / AI Platform
- VP Engineering
- Head of AI Infrastructure / Agent Platform
- CISO / AI Security leadership
- Product or platform leader responsible for agent/tool execution

## First-contact message

Subject: Pre-execution control for AI agent tool execution

I’m reaching out regarding HamidCognition Action Gate, a separately deployable policy-enforcement boundary between an AI agent and protected tools.

The system evaluates actions before execution, binds authorization to tenant, actor, session, and action identity, enforces execution authority, and retains evidence for replay and audit. It supports ALLOW, DENY, ASK, and SANDBOX decisions and includes HTTP and MCP enforcement boundaries.

We are opening a limited number of enterprise proof-of-value engagements focused on a real agent-to-tool execution path.

The proposed pilot is 6–8 weeks and is scoped at $50,000, with the objective of demonstrating the control boundary against customer-selected action scenarios and producing an acceptance/evidence report.

If the use case is relevant, the next step is a technical evaluation under an appropriate NDA.

## NDA boundary

Before sharing source code, internal implementation details, private repository access, signing material, unpublished evidence, or customer-specific deployment credentials, execute a mutually acceptable NDA and written evaluation scope.

## Pilot boundary

The pilot should define in writing:

1. the protected agent and tool path;
2. customer policy scenarios;
3. deployment environment;
4. integration responsibilities;
5. acceptance criteria;
6. evidence to be retained;
7. data handling and residency requirements;
8. support window;
9. IP ownership;
10. permitted use of pilot outputs;
11. conversion terms if the pilot succeeds.

## Commercial guardrails

- Do not promise regulatory certification unless separately evidenced.
- Do not promise universal AI safety or downstream tool safety.
- Do not transfer IP through a pilot by implication.
- Do not grant source-code redistribution or commercialization rights without a written license.
- Do not disclose private credentials or secrets in a sales demonstration.
- Keep the pilot price and scope explicit.

## Target-account sequence

Tier A: agent-security / authorization / control-plane vendors that can embed or license the technology.

Tier B: enterprise AI platform vendors with production tool-using agents.

Tier C: high-consequence enterprises deploying agents against operational systems.

## Demo sequence

1. Agent proposes a protected action.
2. Action reaches Action Gate before the tool.
3. Identity and action context are bound.
4. Policy produces ALLOW, DENY, ASK, or SANDBOX.
5. Execution authority is enforced.
6. Tool executes only when authorized.
7. Evidence is persisted.
8. Replay demonstrates what was authorized and what occurred.

## Positioning

Use: **pre-execution governance and authorization layer for AI agents**.

Avoid: “AI safety solution,” “universal guardrail,” “guaranteed safe agent,” or “replacement for all security controls.”
