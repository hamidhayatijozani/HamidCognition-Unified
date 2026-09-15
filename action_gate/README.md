# HamidCognition Action Gate

**Runtime Action Governance with Replayable Decision Evidence**

This directory contains the executable MVP product candidate. It is deliberately narrower than the broader HamidCognition research program.

## Flow

`Agent -> Action Gate -> Decision -> Tool`

The Gate independently evaluates risk. `risk_hint` from an agent is recorded as untrusted context and cannot lower intrinsic risk.

Decisions:

- `ALLOW`
- `DENY`
- `ASK`
- `SANDBOX`
- `DEFER`

## Executable API

```text
POST /v1/action/evaluate
POST /v1/action/{decision_id}/approve
POST /v1/action/{decision_id}/execution
GET  /v1/evidence/{decision_id}
GET  /v1/replay/{decision_id}
GET  /health
```

## Run locally

```bash
cd action_gate
pip install -r requirements.txt
uvicorn app:app --reload
```

The live three-scenario demo is:

```bash
python demo.py
```

Expected decisions:

```text
delete production file => DENY
external customer email => ASK
financial transfer       => SANDBOX
```

## Enforcement

`enforcement_proxy.py` provides an executable HTTP enforcement mode and an MCP `tools/call` interception mode. The proxy evaluates the action before forwarding it to the tool target.

This is an MVP enforcement adapter, not a claim of protocol-complete MCP production compatibility.

## Evidence and replay

Each evaluation creates an Evidence Record containing request, identity, normalized action, policy version, independent risk assessment, evidence, decision, approval, execution, outcome, timestamp and trace ID. The record is persisted with a SHA-256 evidence fingerprint.

Replay reconstructs the **pre-approval** decision from the recorded request and policy inputs. It does not claim to reproduce arbitrary external-world state.

## Scope boundary

This MVP does not claim that an action is objectively correct or safe. It records and enforces the control decision produced under the available policy, evidence and risk rules.

Research assets such as ClaimLab, Contradiction Ledger and EXP infrastructure remain supporting evidence infrastructure rather than customer-facing product features.
