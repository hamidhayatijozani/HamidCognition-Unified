from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from rate_limit import SlidingWindowRateLimiter
from storage import health as storage_health, init_db, load_record, save_record, consume_nonce, reserve_execution, allow_rate_limit
from canonicalization import KEY_ID, signing_secret_for_key
from csg_routes import router as csg_router

APP_VERSION = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
API_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
SIGNING_SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET")
ENVIRONMENT = os.getenv("ACTION_GATE_ENV", "development").lower()
DECISION_TTL_SECONDS = int(os.getenv("ACTION_GATE_DECISION_TTL_SECONDS", "300"))
APPROVAL_TTL_SECONDS = int(os.getenv("ACTION_GATE_APPROVAL_TTL_SECONDS", "300"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("ACTION_GATE_RATE_LIMIT_PER_MINUTE", "120"))

POLICY_SNAPSHOT = {
    "policy_version": "builtin-v1",
    "high_risk": ["delete_file", "delete_customer", "delete_database", "transfer_funds", "transfer_money"],
    "external": ["send_email", "send_external_email", "http_post_external"],
    "critical": ["transfer_funds", "transfer_money"],
    "rules": ["critical financial action -> SANDBOX", "critical destructive production action -> DENY", "high-risk destructive or external communication -> ASK", "otherwise -> ALLOW"],
}
POLICY_HASH = hashlib.sha256(json.dumps(POLICY_SNAPSHOT, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
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
    if not SIGNING_SECRET:
        if ENVIRONMENT == "production":
            raise HTTPException(503, "production_signing_secret_not_configured")
        return digest(obj)
    return hmac.new(SIGNING_SECRET.encode(), canonical(obj).encode(), hashlib.sha256).hexdigest()


def verify_signature(record: dict[str, Any]) -> bool:
    payload = {"decision_id": record["decision_id"], "tenant_id": record["tenant_id"], "action_hash": record["action_hash"], "policy_hash": record["policy_hash"], "nonce": record["nonce"], "expires_at": record["expires_at"]}
    key_id = record.get("key_id", KEY_ID)
    secret = signing_secret_for_key(key_id)
    if not secret:
        return False
    expected = hmac.new(secret.encode(), canonical(payload).encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, record.get("decision_signature", ""))


def require_auth(authorization: str | None) -> None:
    if ENVIRONMENT == "production" and not API_TOKEN:
        raise HTTPException(503, "production_authentication_not_configured")
    if API_TOKEN is not None and not hmac.compare_digest(authorization or "", f"Bearer {API_TOKEN}"):
        raise HTTPException(401, "invalid_action_gate_credentials")


def enforce_rate_limit(authorization: str | None, tenant_id: str | None) -> None:
    key = f"{tenant_id or 'unknown'}:{authorization or 'anonymous'}"
    if ENVIRONMENT == "production":
        try:
            allowed = allow_rate_limit(key, RATE_LIMIT_PER_MINUTE, 60, time.time())
        except Exception as exc:
            raise HTTPException(503, "rate_limit_store_unavailable") from exc
    else:
        allowed = limiter.allow(key)
    if not allowed:
        raise HTTPException(429, "action_gate_rate_limit_exceeded")


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


class Approval(BaseModel):
    approver_id: str
    approved: bool
    reason: str | None = None
    action_hash: str
    tenant_id: str
    policy_version: str
    ttl_seconds: int | None = None


class ExecutionOutcome(BaseModel):
    action_hash: str
    tenant_id: str
    actor_id: str | None = None
    session_id: str | None = None
    nonce: str
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
    if a in critical:
        return "SANDBOX", [{"policy": "financial-transfer", "result": "SANDBOX", "reason": "critical_action_requires_containment_or_human_review"}]
    if a in high_risk and risk == "CRITICAL":
        return "DENY", [{"policy": "production-destructive-action", "result": "DENY", "reason": "destructive_production_action_blocked"}]
    if a in high_risk or a in external:
        return "ASK", [{"policy": "sensitive-action-approval", "result": "ASK", "reason": "human_approval_required"}]
    return "ALLOW", [{"policy": "default", "result": "ALLOW", "reason": "no_blocking_policy_matched"}]


def normalized_action(req: ActionRequest):
    return {"tenant_id": req.tenant_id, "actor_id": req.actor_id, "session_id": req.session_id, "action": req.action.lower(), "target": req.target, "parameters": req.parameters}


def save(record: dict[str, Any], event_type: str) -> None:
    save_record(record, event_type, digest, canonical, now)


def load(decision_id: str, tenant_id: str):
    raw = load_record(decision_id)
    if not raw:
        raise HTTPException(404, "decision_not_found")
    record = json.loads(raw)
    if record["tenant_id"] != tenant_id:
        raise HTTPException(404, "decision_not_found")
    if not verify_signature(record):
        raise HTTPException(500, "decision_signature_invalid")
    return record


def ensure_live(record: dict[str, Any]):
    if record.get("consumed_at") is not None:
        raise HTTPException(409, "decision_nonce_already_consumed")
    if datetime.fromisoformat(record["expires_at"]) <= datetime.now(timezone.utc):
        raise HTTPException(403, "decision_expired")


@app.get("/health")
def health():
    db_health = storage_health()
    status = "ok" if db_health["status"] == "ok" else "degraded"
    return {"status": status, "product": "HamidCognition Action Gate", "version": APP_VERSION, "policy_hash": POLICY_HASH, "environment": ENVIRONMENT, "storage": db_health}


@app.post("/v1/action/evaluate")
def evaluate(req: ActionRequest, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, req.tenant_id)
    request_id = req.request_id or f"req_{uuid.uuid4().hex}"
    decision_id = f"dec_{uuid.uuid4().hex}"
    trace_id = f"trace_{uuid.uuid4().hex}"
    nonce = uuid.uuid4().hex
    risk, risk_reasons = evaluate_risk(req)
    decision, policy_checks = decide(req, risk)
    normalized = normalized_action(req)
    created = now()
    if DECISION_TTL_SECONDS <= 0 or DECISION_TTL_SECONDS > 86400:
        raise HTTPException(500, "invalid_server_decision_ttl")
    expires = (datetime.now(timezone.utc) + timedelta(seconds=DECISION_TTL_SECONDS)).isoformat()
    action_hash = digest(normalized)
    signature = sign({"decision_id": decision_id, "tenant_id": req.tenant_id, "action_hash": action_hash, "policy_hash": POLICY_HASH, "nonce": nonce, "expires_at": expires})
    record = {
        "schema_version": "action-gate-evidence-3.0",
        "product_version": APP_VERSION,
        "decision_id": decision_id,
        "trace_id": trace_id,
        "request_id": request_id,
        "tenant_id": req.tenant_id,
        "actor_id": req.actor_id,
        "request": req.model_dump(),
        "identity": {"agent_id": req.agent_id, "actor_id": req.actor_id, "session_id": req.session_id},
        "key_id": KEY_ID,
        "normalized_action": normalized,
        "action_hash": action_hash,
        "nonce": nonce,
        "policy_version": POLICY_SNAPSHOT["policy_version"],
        "policy_snapshot": POLICY_SNAPSHOT,
        "policy_hash": POLICY_HASH,
        "risk_assessment": {"level": risk, "reasons": risk_reasons, "agent_risk_hint": req.risk_hint},
        "evidence": req.evidence,
        "decision": decision,
        "policy_checks": policy_checks,
        "constraints": [],
        "approval": None,
        "execution": None,
        "outcome": None,
        "created_at": created,
        "expires_at": expires,
        "consumed_at": None,
        "replay_reference": f"/v1/replay/{decision_id}",
        "decision_signature": signature,
    }
    record["evidence_hash"] = digest(record)
    save(record, "DECISION_CREATED")
    return {k: record[k] for k in ("decision", "decision_id", "request_id", "tenant_id", "actor_id", "risk_assessment", "policy_checks", "evidence", "trace_id", "created_at", "expires_at", "nonce", "action_hash", "policy_version", "policy_hash", "decision_signature", "evidence_hash")} | {"reason": policy_checks[0]["reason"]}


@app.post("/v1/action/{decision_id}/approve")
def approve(decision_id: str, approval: Approval, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, approval.tenant_id)
    record = load(decision_id, approval.tenant_id)
    ensure_live(record)
    if record["decision"] != "ASK":
        raise HTTPException(409, "decision_is_not_awaiting_approval")
    if approval.action_hash != record["action_hash"]:
        raise HTTPException(409, "approval_action_binding_mismatch")
    if approval.policy_version != record["policy_version"]:
        raise HTTPException(409, "approval_policy_binding_mismatch")
    ttl = approval.ttl_seconds if approval.ttl_seconds is not None else APPROVAL_TTL_SECONDS
    if ttl <= 0 or ttl > 86400:
        raise HTTPException(422, "invalid_approval_ttl")
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat()
    record["approval"] = {**approval.model_dump(), "timestamp": now(), "expires_at": expires_at}
    record["decision"] = "ALLOW" if approval.approved else "DENY"
    record["evidence_hash"] = digest(record)
    save(record, "APPROVAL_RECORDED")
    return record


@app.post("/v1/action/{decision_id}/execution/reserve")
def execution_reserve(decision_id: str, outcome: ExecutionOutcome, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, outcome.tenant_id)
    record = load(decision_id, outcome.tenant_id)
    ensure_live(record)
    if record["decision"] != "ALLOW":
        raise HTTPException(403, "execution_not_permitted_by_gate")
    if outcome.action_hash != record["action_hash"]:
        raise HTTPException(409, "execution_action_binding_mismatch")
    if record.get("actor_id") is not None and outcome.actor_id != record.get("actor_id"):
        raise HTTPException(409, "execution_actor_binding_mismatch")
    if record.get("request", {}).get("session_id") is not None and outcome.session_id != record["request"].get("session_id"):
        raise HTTPException(409, "execution_session_binding_mismatch")
    if record.get("request", {}).get("session_id") is not None and outcome.session_id != record["request"].get("session_id"):
        raise HTTPException(409, "execution_session_binding_mismatch")
    if outcome.nonce != record["nonce"]:
        raise HTTPException(409, "execution_nonce_mismatch")
    if record["approval"] and record["approval"].get("approved") and datetime.fromisoformat(record["approval"]["expires_at"]) <= datetime.now(timezone.utc):
        raise HTTPException(403, "approval_expired")
    started_at = now()
    try:
        reserved = reserve_execution(decision_id, outcome.nonce, started_at)
    except Exception as exc:
        raise HTTPException(503, "execution_reservation_store_unavailable") from exc
    if not reserved:
        raise HTTPException(409, "execution_already_reserved_or_consumed")
    record["execution_started_at"] = started_at
    record["execution"] = {"timestamp": started_at, "status": "RESERVED", "action_hash": record["action_hash"], "nonce": record["nonce"]}
    save(record, "EXECUTION_RESERVED")
    return record


@app.post("/v1/action/{decision_id}/execution")
def execution(decision_id: str, outcome: ExecutionOutcome, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, outcome.tenant_id)
    record = load(decision_id, outcome.tenant_id)
    ensure_live(record)
    if record["decision"] != "ALLOW":
        raise HTTPException(403, "execution_not_permitted_by_gate")
    if outcome.action_hash != record["action_hash"]:
        raise HTTPException(409, "execution_action_binding_mismatch")
    if record.get("actor_id") is not None and outcome.actor_id != record.get("actor_id"):
        raise HTTPException(409, "execution_actor_binding_mismatch")
    if outcome.nonce != record["nonce"]:
        raise HTTPException(409, "execution_nonce_mismatch")
    if record["approval"] and record["approval"].get("approved") and datetime.fromisoformat(record["approval"]["expires_at"]) <= datetime.now(timezone.utc):
        raise HTTPException(403, "approval_expired")
    if record.get("execution_started_at") is None:
        raise HTTPException(409, "execution_not_reserved")
    consumed_at = now()
    if not consume_nonce(decision_id, outcome.nonce, consumed_at):
        raise HTTPException(409, "decision_nonce_already_consumed")
    record["execution"] = {"timestamp": consumed_at, "status": "EXECUTED", "action_hash": record["action_hash"], "nonce": record["nonce"]}
    record["outcome"] = outcome.outcome
    record["consumed_at"] = consumed_at
    record["evidence_hash"] = digest(record)
    save(record, "EXECUTION_RECORDED")
    return record


@app.get("/v1/replay/{decision_id}")
def replay(decision_id: str, tenant_id: str, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, tenant_id)
    record = load(decision_id, tenant_id)
    req = ActionRequest.model_validate(record["request"])
    snapshot = record["policy_snapshot"]
    policy_hash_match = digest(snapshot) == record["policy_hash"]
    action_hash_match = digest(normalized_action(req)) == record["action_hash"]
    risk, _ = evaluate_risk(req, snapshot)
    decision, checks = decide(req, risk, snapshot)
    original = record["decision"]
    expected = "ASK" if record["approval"] is not None and original in {"ALLOW", "DENY"} else original
    match = decision == expected and policy_hash_match and action_hash_match
    return {"decision_id": decision_id, "trace_id": record["trace_id"], "replayed_decision": decision, "recorded_preapproval_decision": expected, "match": match, "risk": risk, "policy_checks": checks, "policy_hash": record["policy_hash"], "policy_hash_match": policy_hash_match, "action_hash": record["action_hash"], "action_hash_match": action_hash_match, "evidence_hash": record["evidence_hash"], "audit_event_hash": record.get("audit_event_hash")}


@app.get("/v1/evidence/{decision_id}")
def evidence(decision_id: str, tenant_id: str, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, tenant_id)
    return load(decision_id, tenant_id)
