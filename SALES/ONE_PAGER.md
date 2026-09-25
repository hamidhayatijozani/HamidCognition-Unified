# HamidCognition Action Gate

## Control the action, not just the agent

AI agents can reason, plan, call tools, and change real systems. The security problem begins when a model decision becomes a real-world side effect.

HamidCognition Action Gate is a deployable authorization and evidence boundary placed between an AI agent and protected tools.

**Agent → Action Gate → Protected Tool**

Before execution, Action Gate evaluates the requested action, binds the decision to the relevant tenant/actor/session/action context, records evidence, and issues execution authority only when the policy permits it.

## The buyer problem

Security teams can often observe AI activity without being able to reliably stop an unauthorized tool call at the execution boundary.

The resulting questions are operational, not philosophical:

- Which agent was allowed to perform this action?
- Under which policy?
- For which tenant and session?
- Was the action changed after authorization?
- Can the same authorization be replayed?
- Can a downstream tool be called directly?
- Can an approval be separated from the exact action it approved?
- What evidence remains after an incident?

OWASP identifies excessive agency, excessive permissions and excessive autonomy as material risks for agentic systems and recommends complete mediation at downstream systems. NIST is separately examining identity and authorization for software agents. These are the problems Action Gate is designed to operationalize. 

## What Action Gate adds

- Pre-execution policy decision: ALLOW / DENY / ASK / SANDBOX
- Tenant, actor, session and action binding
- Cryptographically bound decision records
- Gate-issued, time-bounded execution authority
- Single-use nonce / replay protection
- HTTP and MCP enforcement paths
- Fail-closed evidence handling
- Persistent PostgreSQL operation
- Audit and replay evidence
- Acceptance tests for direct bypass and tampering
- Self-hosted, managed and enterprise delivery models

## What makes the product different

Action Gate is not an agent framework and does not attempt to make a model "aligned."

It is a control boundary around the moment where an agent's intent becomes an external action.

The design principle is simple:

> Authorization must be enforceable where the side effect occurs.

## Ideal first customers

1. Companies putting autonomous or semi-autonomous agents into production.
2. Security/platform teams exposing internal APIs, MCP servers or privileged tools to agents.
3. Regulated or high-impact workflows where an unauthorized tool call has material consequences.
4. AI platform teams that need a deployable authorization layer without replacing their existing agent runtime.

## Pilot

A focused pilot should integrate one high-impact tool or MCP server.

Pilot success is measured by executable acceptance tests, not by a slide deck:

- direct downstream access is rejected;
- authority is bound to tenant/action/policy;
- replay is rejected;
- expiry is enforced;
- tampering is rejected;
- evidence survives restart;
- the customer can reproduce the acceptance result.

## Delivery

**SELF_HOSTED** — customer-operated deployment.

**MANAGED** — HamidCognition-operated service boundary.

**ENTERPRISE** — negotiated integration, security review, support, deployment architecture and SLA.

Security and compliance claims remain scoped to the controls actually evidenced in the customer's deployment.
