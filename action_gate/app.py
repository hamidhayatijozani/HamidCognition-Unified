from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from rate_limit import SlidingWindowRateLimiter
from storage import health as storage_health, init_db, load_record, save_record, finalize_execution, reconcile_execution, reserve_execution, allow_rate_limit
from csg_routes import router as csg_router
from keyring import configured_key_ids, current_key_id, current_secret, verify_with_keyring
from policy_store import load_policy, policy_hash
from security_authority import issue_authority

APP_VERSION = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
API_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
SIGNING_SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET")
ENVIRONMENT = os.getenv("ACTION_GATE_ENV", "development").lower()
DECISION_TTL_SECONDS = int(os.getenv("ACTION_GATE_DECISION_TTL_SECONDS", "300"))
APPROVAL_TTL_SECONDS = int(os.getenv("ACTION_GATE_APPROVAL_TTL_SECONDS", "300"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("ACTION_GATE_RATE_LIMIT_PER_MINUTE", "120"))
APPROVAL_SECRET = os.getenv("ACTION_GATE_APPROVAL_SECRET")
REQUIRE_SESSION_BINDING = os.getenv("ACTION_GATE_REQUIRE_SESSION_BINDING", "1" if ENVIRONMENT == "production" else "0") == "1"

POLICY_SNAPSHOT = load_policy()
POLICY_HASH = policy_hash(POLICY_SNAPSHOT)
app = FastAPI(title="HamidCognition Action Gate", version=APP_VERSION)
app.include_router(csg_router)
limiter = SlidingWindowRateLimiter(RATE_LIMIT_PER_MINUTE, 60)


@app.on_event("startup")
def startup() -> None:
    init_db()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def sign(obj: Any) -> str:
    secret = SIGNING_SECRET or current_secret()
    if not secret:
        if ENVIRONMENT == "production":
            raise HTTPException(503, "production_signing_secret_not_configured")
        return digest(obj)
    return hmac.new(secret.encode(), canonical(obj).encode(), hashlib.sha256).hexdigest()


def approval_payload(approval: Approval) -> dict[str, Any]:
    return {k: v for k, v in approval.model_dump(exclude_none=True).items() if k != "approval_signature"}


def verify_approval_signature(approval: Approval) -> bool:
    if not APPROVAL_SECRET:
        return False
    expected = hmac.new(APPROVAL_SECRET.encode(), canonical(approval_payload(approval)).encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, approval.approval_signature or "")


def verify_signature(record: dict[str, Any]) -> bool:
    payload = {"decision_id": record["decision_id"], "tenant_id": record["tenant_id"], "action_hash": record["action_hash"], "policy_hash": record["policy_hash"], "nonce": record["nonce"], "expires_at": record["expires_at"]}
    if verify_with_keyring(payload, record.get("decision_signature", ""), record.get("key_id", current_key_id())):
        return True
    try:
        return hmac.compare_digest(sign(payload), record.get("decision_signature", ""))
    except HTTPException:
        return False


def require_auth(authorization: str | None) -> None:
    if ENVIRONMENT == "production" and not API_TOKEN:
        raise HTTPException(503, "production_authentication_not_configured")
    if API_TOKEN is not None and not hmac.compare_digest(authorization or "", f"Bearer {API_TOKEN}"):
        raise HTTPException(401, "invalid_action_gate_credentials")


def enforce_rate_limit(authorization: str | None, tenant_id: str | None) -> None:
    credential_fingerprint = hashlib.sha256((authorization or "anonymous").encode()).hexdigest()
    key = f"{tenant_id or 'unknown'}:{credential_fingerprint}"
    if ENVIRONMENT == "production":
        try:
            allowed = allow_rate_limit(key, RATE_LIMIT_PER_MINUTE, 60, time.time())
        except Exception as exc:
            raise HTTPException(503, "rate_limit_store_unavailable") from exc
    else:
        allowed = limiter.allow(key)
    if not allowed:
        raise HTTPException(429, "action_gate_rate_limit_exceeded")


class PreExecutionSignal(BaseModel):
    mode: Literal["PROCEED", "INHIBIT", "HOLD", "UNKNOWN"]
    reactivity: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1, max_length=256)
    consumer_action: Literal[
        "REQUEST_ACTION_GATE_AUTHORIZATION",
        "BLOCK_REACTION",
        "REQUIRE_REEVALUATION",
        "REQUIRE_EVIDENCE",
    ]

    @classmethod
    def validate_consumer_action(cls, mode: str, consumer_action: str) -> bool:
        expected = {
            "PROCEED": "REQUEST_ACTION_GATE_AUTHORIZATION",
            "INHIBIT": "BLOCK_REACTION",
            "HOLD": "REQUIRE_REEVALUATION",
            "UNKNOWN": "REQUIRE_EVIDENCE",
        }
        return expected[mode] == consumer_action


class ActionRequest(BaseModel):
    request_id: str | None = None
    tenant_id: str
    agent_id: str
    actor_id: str | None = None
    session_id: str | None = None
    action: str
    target: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    risk_hint: str | None = None
    pre_execution_signal: PreExecutionSignal | None = None


class Approval(BaseModel):
    approver_id: str
    approved: bool
    reason: str | None = None
    action_hash: str
    tenant_id: str
    policy_version: str
    ttl_seconds: int | None = None
    approval_signature: str | None = None


class ExecutionOutcome(BaseModel):
    action_hash: str
    tenant_id: str
    actor_id: str | None = None
    session_id: str | None = None
    nonce: str
    outcome: dict[str, Any] = Field(default_factory=dict)


class ReconciliationOutcome(BaseModel):
    action_hash: str
    tenant_id: str
    nonce: str
    resolution: str
    outcome: dict[str, Any] = Field(default_factory=dict)


def policy_sets(snapshot: dict[str, Any]):
    return set(snapshot["high_risk"]), set(snapshot["external"]), set(snapshot["critical"])


def evaluate_risk(req: ActionRequest, snapshot: dict[str, Any] = POLICY_SNAPSHOT):
    high_risk, external, critical = policy_sets(snapshot)
    a = req.action.lower()
    if a in critical:
        return "CRITICAL", ["financial_transfer_is_inherently_high_risk"]
    if a in high_risk:
        reasons = ["destructive_action"]
        if req.target and ("production" in req.target.lower() or "prod" in req.target.lower()):
            reasons.append("production_target")
            return "CRITICAL", reasons
        return "HIGH", reasons
    if a in external:
        return "HIGH", ["external_communication"]
    return "LOW", ["no_intrinsic_high_risk_rule_matched"]


def decide(req: ActionRequest, risk: str, snapshot: dict[str, Any] = POLICY_SNAPSHOT):
    high_risk, external, critical = policy_sets(snapshot)
    a = req.action.lower()

    if req.pre_execution_signal is not None:
        signal = req.pre_execution_signal
        if not PreExecutionSignal.validate_consumer_action(signal.mode, signal.consumer_action):
            raise HTTPException(422, "invalid_pre_execution_signal_binding")
        if signal.mode == "INHIBIT":
            return "DENY", [{
                "policy": "pre-execution-signal",
                "result": "DENY",
                "reason": "pre_execution_signal_inhibit",
                "signal_mode": signal.mode,
                "signal_reactivity": signal.reactivity,
                "signal_reason": signal.reason,
            }]
        if signal.mode in {"HOLD", "UNKNOWN"}:
            return "ASK", [{
                "policy": "pre-execution-signal",
                "result": "ASK",
                "reason": f"pre_execution_signal_{signal.mode.lower()}",
                "signal_mode": signal.mode,
                "signal_reactivity": signal.reactivity,
                "signal_reason": signal.reason,
            }]
        # PROCEED never grants authority. Normal Action Gate policy still decides.

    if a in critical:
        return "SANDBOX", [{"policy": "financial-transfer", "result": "SANDBOX", "reason": "critical_action_requires_containment_or_human_review"}]
    if a in high_risk and risk == "CRITICAL":
        return "DENY", [{"policy": "production-destructive-action", "result": "DENY", "reason": "destructive_production_action_blocked"}]
    if a in high_risk or a in external:
        return "ASK", [{"policy": "sensitive-action-approval", "result": "ASK", "reason": "human_approval_required"}]
    return "ALLOW", [{"policy": "default", "result": "ALLOW", "reason": "no_blocking_policy_matched"}]

