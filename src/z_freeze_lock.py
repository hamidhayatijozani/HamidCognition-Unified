"""Z-FREEZE-LOCK v2 reference policy engine.

Deterministic policy evaluation. No network, shell, model-control, or secret access.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from hashlib import sha256
import json
from typing import Any


PACKAGE_ID = "Z-FREEZE-LOCK"
VERSION = "2.0.0"
STAMP = "HAMID-ALPHA"

ALLOWED = {"RAFA_FREEZE", "AUDIT_DEEP", "ACK_REGISTER", "ROLLBACK_LAYER", "MERGE_SAFE"}

class TruthState(str, Enum):
    SPECIFIED = "SPECIFIED"
    SIMULATED = "SIMULATED"
    ENFORCED = "ENFORCED"

class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"

@dataclass(frozen=True)
class Result:
    decision: Decision
    truth_state: TruthState
    reason: str
    side_effects: bool = False
    audit_required: bool = True

    def json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)

def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()

def content_hash(obj: Any) -> str:
    return sha256(canonical_bytes(obj)).hexdigest()

def validate_command(cmd: dict[str, Any]) -> list[str]:
    required = {"action", "payload", "signer", "moduleId", "requestId"}
    missing = sorted(required - cmd.keys())
    if missing:
        return [f"missing:{x}" for x in missing]
    errors = []
    if not isinstance(cmd["action"], str):
        errors.append("action_not_string")
    if cmd["action"] not in ALLOWED:
        errors.append("action_not_allowed")
    if cmd["signer"] != STAMP:
        errors.append("signer_mismatch")
    if not isinstance(cmd["moduleId"], str) or not cmd["moduleId"]:
        errors.append("module_invalid")
    if not isinstance(cmd["requestId"], str) or not cmd["requestId"]:
        errors.append("request_id_invalid")
    return errors

def evaluate(cmd: dict[str, Any], *, simulation_ok: bool = True,
             runtime_enforced: bool = False) -> Result:
    errors = validate_command(cmd)
    if errors:
        return Result(Decision.DENY, TruthState.ENFORCED if runtime_enforced else TruthState.SIMULATED,
                      ";".join(errors))
    if not simulation_ok:
        return Result(Decision.DENY, TruthState.ENFORCED if runtime_enforced else TruthState.SIMULATED,
                      "simulation_failed")
    state = TruthState.ENFORCED if runtime_enforced else TruthState.SIMULATED
    return Result(Decision.ALLOW, state, "schema_ok;auth_ok;policy_ok;simulation_ok")

def audit_event(cmd: dict[str, Any], result: Result) -> dict[str, Any]:
    return {
        "packageId": PACKAGE_ID,
        "version": VERSION,
        "requestId": cmd.get("requestId"),
        "moduleId": cmd.get("moduleId"),
        "action": cmd.get("action"),
        **asdict(result),
    }

if __name__ == "__main__":
    import sys
    command = json.load(sys.stdin)
    result = evaluate(command)
    print(json.dumps(audit_event(command, result), ensure_ascii=False, sort_keys=True))
