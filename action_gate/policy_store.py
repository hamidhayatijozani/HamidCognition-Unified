from __future__ import annotations

import hashlib
import json
import os
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "policy_version": "builtin-v1",
    "high_risk": ["delete_file", "delete_customer", "delete_database", "transfer_funds", "transfer_money"],
    "external": ["send_email", "send_external_email", "http_post_external"],
    "critical": ["transfer_funds", "transfer_money"],
    "rules": [
        "critical financial action -> SANDBOX",
        "critical destructive production action -> DENY",
        "high-risk destructive or external communication -> ASK",
        "otherwise -> ALLOW",
    ],
}


def load_policy() -> dict[str, Any]:
    raw = os.getenv("ACTION_GATE_POLICY_JSON")
    if not raw:
        return dict(DEFAULT_POLICY)
    try:
        policy = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("invalid_action_gate_policy_json") from exc
    if not isinstance(policy, dict):
        raise RuntimeError("action_gate_policy_must_be_object")
    required = {"policy_version", "high_risk", "external", "critical", "rules"}
    if not required.issubset(policy):
        raise RuntimeError("action_gate_policy_missing_required_fields")
    if not isinstance(policy["policy_version"], str) or not policy["policy_version"]:
        raise RuntimeError("invalid_action_gate_policy_version")
    for field in ("high_risk", "external", "critical", "rules"):
        if not isinstance(policy[field], list) or not all(isinstance(v, str) and v for v in policy[field]):
            raise RuntimeError(f"invalid_action_gate_policy_{field}")
    return policy


def policy_hash(policy: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
