"""Contract-first execution latch for the HHJ-CSG vertical slice.

This module is a simulated executor boundary. It performs no external side effect.
It proves the narrower invariant: an execution receipt can only be created for a
fresh, signed Decision Object bound to the exact Permission Request, and the same
nonce cannot be consumed twice in this process.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Mapping

try:
    from .contract import decision_signing_payload, hmac_sha256, sha256_digest, verify_hmac
    from .execution_receipt import make_receipt, validate_receipt
except ImportError:
    from contract import decision_signing_payload, hmac_sha256, sha256_digest, verify_hmac
    from execution_receipt import make_receipt, validate_receipt

EXECUTABLE = frozenset({"ALLOW", "SANDBOX"})
_consumed_nonces: set[str] = set()
_nonce_lock = threading.Lock()


def action_hash(request: Mapping[str, Any]) -> str:
    return sha256_digest({
        "tenant_id": request["tenant_id"],
        "agent_id": request["agent_id"],
        "action": request["action"],
        "target": request["target"],
        "parameters": request["parameters"],
    })


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def validate_execution_authorization(
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    secret: str,
    now: datetime | None = None,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        expected_request_digest = sha256_digest(dict(request))
        if decision.get("request_digest") != expected_request_digest:
            errors.append("binding:request_digest_mismatch")
        expected_decision_digest = sha256_digest({k: v for k, v in decision.items() if k not in {"decision_digest", "signature"}})
        if decision.get("decision_digest") != expected_decision_digest:
            errors.append("integrity:decision_digest_mismatch")
        if not verify_hmac(decision_signing_payload(decision), str(decision.get("signature", "")), secret):
            errors.append("auth:decision_signature_invalid")
        if decision.get("decision") not in EXECUTABLE:
            errors.append(f"execution:not_executable_decision:{decision.get('decision')}")
        if decision.get("key_id") is None or decision.get("signature_algorithm") != "HMAC-SHA256":
            errors.append("auth:unsupported_signature_contract")
        issued = _parse_time(str(decision["issued_at"]))
        expires = _parse_time(str(decision["expires_at"]))
        reference = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if issued > reference:
            errors.append("freshness:issued_in_future")
        if expires <= reference:
            errors.append("freshness:decision_expired")
        if expires <= issued:
            errors.append("freshness:invalid_expiry_interval")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"decision:invalid:{exc}")
    return not errors, errors


def execute_simulated(
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    secret: str,
    executor_id: str = "hhj-csg-simulated-executor",
    now: datetime | None = None,
) -> dict[str, Any]:
    valid, errors = validate_execution_authorization(request, decision, secret=secret, now=now)
    if not valid:
        raise ValueError(";".join(errors))
    nonce = str(decision["nonce"])
    with _nonce_lock:
        if nonce in _consumed_nonces:
            raise ValueError("execution:nonce_already_consumed")
        _consumed_nonces.add(nonce)

    started = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    finished = datetime.now(timezone.utc).isoformat()
    ahash = action_hash(request)
    receipt = make_receipt(
        request=request,
        request_digest=decision["request_digest"],
        decision_id=decision["decision_id"],
        decision_digest=decision["decision_digest"],
        action_hash=ahash,
        nonce=nonce,
        executor_id=executor_id,
        started_at=started,
        finished_at=finished,
        status="EXECUTED",
        outcome={"mode": "SIMULATED", "action": request["action"], "target": request["target"]},
    )
    receipt_result = validate_receipt(
        receipt,
        request=request,
        request_digest=decision["request_digest"],
        decision_id=decision["decision_id"],
        decision_digest=decision["decision_digest"],
        action_hash=ahash,
        nonce=nonce,
        expected_executor_id=executor_id,
    )
    if not receipt_result.valid:
        raise ValueError("receipt:invalid:" + ";".join(receipt_result.errors))
    return receipt


def reset_nonce_ledger() -> None:
    with _nonce_lock:
        _consumed_nonces.clear()
