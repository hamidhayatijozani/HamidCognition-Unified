"""Controlled agent/tool harness for exercising HamidCognition's Action Gate.

This does not claim to intercept the ChatGPT runtime itself. It models the
boundary that a ChatGPT/MCP client would cross before a protected action.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# The production gate expects these values to exist before import/runtime use.
os.environ.setdefault("ACTION_GATE_ENV", "production")
os.environ.setdefault("ACTION_GATE_API_TOKEN", "chatgpt-harness-token")
os.environ.setdefault("ACTION_GATE_SIGNING_SECRET", "chatgpt-harness-signing-secret")
os.environ.setdefault("ACTION_GATE_APPROVAL_SECRET", "chatgpt-harness-approval-secret")
os.environ.setdefault("ACTION_GATE_ENFORCEMENT_SECRET", "chatgpt-harness-enforcement-secret")
os.environ.setdefault("ACTION_GATE_DB", "/tmp/hamidcognition-chatgpt-harness.db")
os.environ.setdefault("ACTION_GATE_REQUIRE_SESSION_BINDING", "1")


def main() -> int:
    from action_gate.security_authority import Authority, canonical_digest, sign_authority

    tenant = "chatgpt-harness-tenant"
    action = "protected.tool.write"
    policy = "policy.production.v1"
    nonce = "chatgpt-harness-nonce-001"

    authority = Authority(
        tenant_id=tenant,
        action=action,
        policy_id=policy,
        decision="ALLOW",
        issued_at=1700000000,
        expires_at=4102444800,
        nonce=nonce,
    )
    secret = os.environ["ACTION_GATE_SIGNING_SECRET"].encode()
    signed = sign_authority(authority, secret)

    print("HAMIDCOGNITION CHATGPT-STYLE ACTION GATE HARNESS")
    print(f"decision={signed.decision}")
    print(f"tenant={signed.tenant_id}")
    print(f"action={signed.action}")
    print(f"policy={signed.policy_id}")
    print(f"nonce={signed.nonce}")
    print(f"authority_digest={canonical_digest(signed)}")
    print("boundary=agent -> action-gate -> protected-tool")
    print("runtime_interception=false")
    print("evidence_mode=deterministic-harness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
