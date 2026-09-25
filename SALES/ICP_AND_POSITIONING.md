# Ideal Customer Profile and Positioning

## Primary ICP

### Security / Platform Engineering
**Trigger:** the organization is deploying agents with write access to internal systems, APIs, cloud resources, databases or MCP tools.

**Pain:** existing controls authenticate the agent but do not bind authorization to the exact action at execution time.

**Buyer:** CISO, VP Security, Head of AI Security, Platform Security lead, or engineering leader responsible for agent infrastructure.

**Technical champion:** AI platform, security engineering, DevSecOps or infrastructure team.

### AI Platform Teams
**Trigger:** the team already has an agent runtime and needs a security boundary without replacing it.

**Message:** keep the existing agent. Put Action Gate between the agent and the protected tool.

### High-impact workflows
Examples include financial operations, privileged administration, production changes, customer communications, data mutation and other irreversible actions.

## Positioning

Do not sell "AI safety."

Sell a narrower, testable product:

**Runtime authorization for agent tool execution.**

The core commercial statement:

> HamidCognition Action Gate gives security teams an enforceable authorization boundary between an AI agent and the tools that can change real systems.

## Category

Recommended category language:

**Agent Runtime Authorization & Execution Governance**

Avoid positioning the product as:
- a general-purpose AI safety platform;
- an LLM firewall;
- an IAM replacement;
- an agent framework;
- a compliance certification;
- a guarantee against prompt injection.

## Competitive conversation

The question is not "Does another product also monitor agents?"

The useful distinction is:

**Can the control point prevent a protected downstream tool from accepting an unauthorized or replayed action, and can the customer prove that behavior with executable evidence?**

This keeps the conversation tied to a concrete acceptance boundary instead of vendor feature-counting.
