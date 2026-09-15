"""Execution Receipt: immutable linkage between validated intent and observed execution."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json
from typing import Any, Mapping

RECEIPT_VERSION = "ER-0.1"

def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def parse_time(value: str) -> datetime:
    if not isinstance(value, str): raise ValueError("timestamp must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None: raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)

@dataclass(frozen=True)
class ReceiptValidation:
    valid: bool
    errors: tuple[str, ...]
    receipt_version: str = RECEIPT_VERSION
    def as_dict(self) -> dict[str, Any]: return asdict(self) | {"errors": list(self.errors)}

def make_receipt(*, request: Mapping[str, Any], request_digest: str, decision_id: str,
                 decision_digest: str, action_hash: str, nonce: str, executor_id: str,
                 started_at: str, finished_at: str, status: str,
                 outcome: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if status not in {"EXECUTED", "FAILED", "REJECTED"}: raise ValueError("invalid execution status")
    body = {"receipt_version": RECEIPT_VERSION, "request_digest": request_digest,
            "decision_id": decision_id, "decision_digest": decision_digest,
            "action_hash": action_hash, "nonce": nonce, "executor_id": executor_id,
            "started_at": started_at, "finished_at": finished_at, "status": status,
            "outcome": dict(outcome or {})}
    body["receipt_digest"] = digest(body)
    return body

def validate_receipt(receipt: Mapping[str, Any], *, request: Mapping[str, Any],
                     request_digest: str, decision_id: str, decision_digest: str,
                     action_hash: str, nonce: str,
                     expected_executor_id: str | None = None) -> ReceiptValidation:
    errors: list[str] = []
    required = ("receipt_version", "request_digest", "decision_id", "decision_digest",
                "action_hash", "nonce", "executor_id", "started_at", "finished_at",
                "status", "outcome", "receipt_digest")
    for key in required:
        if key not in receipt: errors.append(f"missing:{key}")
    if errors: return ReceiptValidation(False, tuple(errors))
    if receipt["receipt_version"] != RECEIPT_VERSION: errors.append("version:unsupported")
    if receipt["request_digest"] != request_digest: errors.append("binding:request_digest_mismatch")
    if receipt["decision_id"] != decision_id: errors.append("binding:decision_id_mismatch")
    if receipt["decision_digest"] != decision_digest: errors.append("binding:decision_digest_mismatch")
    if receipt["action_hash"] != action_hash: errors.append("binding:action_hash_mismatch")
    if receipt["nonce"] != nonce: errors.append("binding:nonce_mismatch")
    if not isinstance(receipt["executor_id"], str) or not receipt["executor_id"].strip(): errors.append("executor:missing")
    if expected_executor_id is not None and receipt["executor_id"] != expected_executor_id: errors.append("executor:identity_mismatch")
    try:
        started, finished = parse_time(receipt["started_at"]), parse_time(receipt["finished_at"])
        if finished < started: errors.append("time:finished_before_started")
    except (TypeError, ValueError) as exc: errors.append(f"time:invalid:{exc}")
    if receipt["status"] not in {"EXECUTED", "FAILED", "REJECTED"}: errors.append("status:invalid")
    unsigned = {k: receipt[k] for k in required if k != "receipt_digest"}
    if receipt["receipt_digest"] != digest(unsigned): errors.append("integrity:receipt_digest_mismatch")
    if not isinstance(request, Mapping): errors.append("request:invalid")
    return ReceiptValidation(not errors, tuple(errors))
