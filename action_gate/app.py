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
from pydantic import BaseModel, ConfigDict, Field

from rate_limit import SlidingWindowRateLimiter
from storage import health as storage_health, init_db, load_record, save_record, finalize_execution, reconcile_execution, reserve_execution, allow_rate_limit
from csg_routes import router as csg_router
from keyring import configured_key_ids, current_key_id, current_secret, verify_with_keyring
from policy_store import load_policy, policy_hash
from security_authority import issue_authority
from state_oracle import STATE_ORACLE_SECRET, commit_snapshot, get_current_snapshot, verify_commit_signature

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
    model_config = ConfigDict(extra="forbid")

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
    world_version: str | None = None


class Approval(BaseModel):
    approver_id: str
    approved: bool
    reason: str | None = None
    action_hash: str
    tenant_id: str
    policy_version: str
    ttl_seconds: int | None = None
    approval_signature: str | None = None


class FactState(BaseModel):
    """Evidence truth-state metadata. State is explicit and never inferred as trust."""
    state: Literal["FACT", "VERIFIED_FACT", "OBSERVATION", "DERIVED", "PREDICTION", "CLAIM", "UNKNOWN", "STALE", "CONTRADICTED"]
    source: str | None = None
    observed_at: str | None = None
    expires_at: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


def normalize_evidence(evidence: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Normalize evidence state and detect explicit contradictions without inventing facts."""
    normalized: list[dict[str, Any]] = []
    contradictions: list[dict[str, Any]] = []
    seen: dict[str, tuple[Any, str]] = {}
    allowed = {"FACT", "VERIFIED_FACT", "OBSERVATION", "DERIVED", "PREDICTION", "CLAIM", "UNKNOWN", "STALE", "CONTRADICTED"}

    for item in evidence:
        row = dict(item)
        state = str(row.get("state", "UNKNOWN")).upper()
        if state not in allowed:
            state = "UNKNOWN"
        row["state"] = state

        key = row.get("key") or row.get("subject") or row.get("name")
        if key is not None and "value" in row:
            key = str(key)
            value = row.get("value")
            if key in seen and seen[key][0] != value:
                contradiction = {
                    "key": key,
                    "previous_value": seen[key][0],
                    "current_value": value,
                    "previous_state": seen[key][1],
                    "current_state": state,
                    "reason": "conflicting_evidence_values",
                }
                contradictions.append(contradiction)
            else:
                seen[key] = (value, state)

        expires_at = row.get("expires_at")
        if expires_at:
            try:
                if datetime.fromisoformat(str(expires_at)) <= datetime.now(timezone.utc):
                    row["state"] = "STALE"
            except ValueError:
                row["state"] = "UNKNOWN"

        normalized.append(row)

    return normalized, contradictions


def evidence_gate(evidence: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    normalized, contradictions = normalize_evidence(evidence)
    blocking_states = {"UNKNOWN", "STALE", "CONTRADICTED"}
    blocking = [x for x in normalized if x.get("state") in blocking_states]
    return ("BLOCK" if contradictions or blocking else "PASS", normalized, contradictions)


class ExecutionOutcome(BaseModel):
    action_hash: str
    tenant_id: str
    actor_id: str | None = None
    session_id: str | None = None
    nonce: str
    world_version: str | None = None
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


def compute_signal(
    req: ActionRequest,
    risk: str,
    snapshot: dict[str, Any] = POLICY_SNAPSHOT,
) -> PreExecutionSignal:
    high_risk, external, _critical = policy_sets(snapshot)
    a = req.action.lower()
    if risk == "CRITICAL":
        return PreExecutionSignal(
            mode="INHIBIT",
            reactivity=1.0,
            reason="critical_risk_detected",
            consumer_action="BLOCK_REACTION",
        )
    if risk == "HIGH" and a in high_risk:
        return PreExecutionSignal(
            mode="HOLD",
            reactivity=0.75,
            reason="high_risk_action_requires_review",
            consumer_action="REQUIRE_REEVALUATION",
        )
    if not req.evidence and (a in high_risk or a in external):
        return PreExecutionSignal(
            mode="UNKNOWN",
            reactivity=0.5,
            reason="no_evidence_for_high_risk_action",
            consumer_action="REQUIRE_EVIDENCE",
        )
    return PreExecutionSignal(
        mode="PROCEED",
        reactivity=0.1,
        reason="default_proceed",
        consumer_action="REQUEST_ACTION_GATE_AUTHORIZATION",
    )


def decide(
    req: ActionRequest,
    risk: str,
    signal: PreExecutionSignal,
    snapshot: dict[str, Any] = POLICY_SNAPSHOT,
):
    high_risk, external, critical = policy_sets(snapshot)
    a = req.action.lower()

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

    if a in critical:
        return "SANDBOX", [{"policy": "financial-transfer", "result": "SANDBOX", "reason": "critical_action_requires_containment_or_human_review"}]
    if a in high_risk and risk == "CRITICAL":
        return "DENY", [{"policy": "production-destructive-action", "result": "DENY", "reason": "destructive_production_action_blocked"}]
    if a in high_risk or a in external:
        return "ASK", [{"policy": "sensitive-action-approval", "result": "ASK", "reason": "human_approval_required"}]
    return "ALLOW", [{"policy": "default", "result": "ALLOW", "reason": "no_blocking_policy_matched"}]


def decide_legacy(req: ActionRequest, risk: str, snapshot: dict[str, Any] = POLICY_SNAPSHOT, signal: PreExecutionSignal | None = None):
    high_risk, external, critical = policy_sets(snapshot)
    a = req.action.lower()

    if signal is not None:
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

    if a in critical:
        return "SANDBOX", [{"policy": "financial-transfer", "result": "SANDBOX", "reason": "critical_action_requires_containment_or_human_review"}]
    if a in high_risk and risk == "CRITICAL":
        return "DENY", [{"policy": "production-destructive-action", "result": "DENY", "reason": "destructive_production_action_blocked"}]
    if a in high_risk or a in external:
        return "ASK", [{"policy": "sensitive-action-approval", "result": "ASK", "reason": "human_approval_required"}]
    return "ALLOW", [{"policy": "default", "result": "ALLOW", "reason": "no_blocking_policy_matched"}]


def normalized_action(req: ActionRequest, signal: PreExecutionSignal | None = None) -> dict[str, Any]:
    if signal is None:
        risk, _ = evaluate_risk(req)
        signal = compute_signal(req, risk)
    normalized = {
        "tenant_id": req.tenant_id,
        "actor_id": req.actor_id,
        "session_id": req.session_id,
        "action": req.action.lower(),
        "target": req.target,
        "parameters": req.parameters,
        "pre_execution_signal": signal.model_dump(),
    }
    return normalized


def legacy_normalized_action(req: ActionRequest, signal: PreExecutionSignal | None = None) -> dict[str, Any]:
    normalized = {
        "tenant_id": req.tenant_id,
        "actor_id": req.actor_id,
        "session_id": req.session_id,
        "action": req.action.lower(),
        "target": req.target,
        "parameters": req.parameters,
    }
    if signal is not None:
        normalized["pre_execution_signal"] = signal.model_dump()
    return normalized


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


@app.get("/v1/state/current")
def state_current(authorization: str | None = Header(default=None)):
    require_auth(authorization)
    current = get_current_snapshot()
    if current is None:
        raise HTTPException(503, "state_oracle_not_initialized")
    return {k: current[k] for k in ("snapshot_id", "world_version", "snapshot_hash", "committed_at")}


class StateSnapshotRequest(BaseModel):
    world_version: str
    snapshot: dict[str, Any] = Field(default_factory=dict)
    oracle_signature: str


@app.post("/v1/state/commit")
def state_commit(req: StateSnapshotRequest, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    if ENVIRONMENT == "production" and not STATE_ORACLE_SECRET:
        raise HTTPException(503, "production_state_oracle_secret_not_configured")
    payload = {"world_version": req.world_version, "snapshot": req.snapshot}
    if not verify_commit_signature(payload, req.oracle_signature):
        raise HTTPException(401, "state_oracle_signature_invalid")
    try:
        return commit_snapshot(req.snapshot, req.world_version)
    except Exception as exc:
        raise HTTPException(503, "state_oracle_commit_failed") from exc


@app.get("/health")
def health():
    db_health = storage_health()
    status = "ok" if db_health["status"] == "ok" else "degraded"
    current_state = get_current_snapshot()
    return {"status": status if current_state is not None or ENVIRONMENT != "production" else "degraded", "product": "HamidCognition Action Gate", "version": APP_VERSION, "policy_hash": POLICY_HASH, "policy_version": POLICY_SNAPSHOT["policy_version"], "key_ids": configured_key_ids(), "current_key_id": current_key_id(), "environment": ENVIRONMENT, "storage": db_health, "state_oracle": {"status": "ready" if current_state else "uninitialized", "world_version": current_state["world_version"] if current_state else None}}


@app.post("/v1/action/evaluate")
def evaluate(req: ActionRequest, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, req.tenant_id)
    request_id = req.request_id or f"req_{uuid.uuid4().hex}"
    if ENVIRONMENT == "production" and not (SIGNING_SECRET or current_secret()):
        raise HTTPException(503, "production_signing_secret_not_configured")
    if ENVIRONMENT == "production" and not req.actor_id:
        raise HTTPException(422, "actor_id_required")
    if REQUIRE_SESSION_BINDING and not req.session_id:
        raise HTTPException(422, "session_id_required")
    decision_id = f"dec_{uuid.uuid4().hex}"
    trace_id = f"trace_{uuid.uuid4().hex}"
    nonce = uuid.uuid4().hex
    risk, risk_reasons = evaluate_risk(req)
    signal = compute_signal(req, risk)
    current_state = get_current_snapshot()
    if current_state is None:
        if ENVIRONMENT == "production":
            raise HTTPException(503, "state_oracle_not_initialized")
    else:
        if req.world_version is not None and req.world_version != current_state["world_version"]:
            raise HTTPException(409, "request_world_version_is_not_current")
        req.world_version = current_state["world_version"]
    evidence_status, normalized_evidence, contradictions = evidence_gate(req.evidence)
    if contradictions:
        decision = "ASK"
        policy_checks = [{
            "policy": "evidence-integrity",
            "result": "ASK",
            "reason": "contradictory_evidence_requires_recheck",
            "contradictions": contradictions,
        }]
    elif evidence_status == "BLOCK":
        decision = "ASK"
        policy_checks = [{
            "policy": "evidence-integrity",
            "result": "ASK",
            "reason": "unknown_or_stale_evidence_requires_recheck",
        }]
    else:
        decision, policy_checks = decide(req, risk, signal)
    req.evidence = normalized_evidence
    normalized = normalized_action(req, signal)
    created = now()
    if DECISION_TTL_SECONDS <= 0 or DECISION_TTL_SECONDS > 86400:
        raise HTTPException(500, "invalid_server_decision_ttl")
    expires = (datetime.now(timezone.utc) + timedelta(seconds=DECISION_TTL_SECONDS)).isoformat()
    action_hash = digest(normalized)
    signature = sign({"decision_id": decision_id, "tenant_id": req.tenant_id, "action_hash": action_hash, "policy_hash": POLICY_HASH, "nonce": nonce, "expires_at": expires})
    record = {
        "schema_version": "action-gate-evidence-3.1",
        "product_version": APP_VERSION,
        "decision_id": decision_id,
        "trace_id": trace_id,
        "request_id": request_id,
        "tenant_id": req.tenant_id,
        "actor_id": req.actor_id,
        "session_id": req.session_id,
        "request": req.model_dump(),
        "identity": {"agent_id": req.agent_id, "actor_id": req.actor_id, "session_id": req.session_id},
        "normalized_action": normalized,
        "action_hash": action_hash,
        "nonce": nonce,
        "policy_version": POLICY_SNAPSHOT["policy_version"],
        "policy_snapshot": POLICY_SNAPSHOT,
        "policy_hash": POLICY_HASH,
        "key_id": current_key_id(),
        "risk_assessment": {"level": risk, "reasons": risk_reasons, "agent_risk_hint": req.risk_hint},
        "evidence": req.evidence,
        "decision": decision,
        "policy_checks": policy_checks,
        "pre_execution_signal": signal.model_dump(),
        "constraints": [
            {"name": "unknown_is_not_allow", "enforced": True},
            {"name": "stale_is_not_allow", "enforced": True},
            {"name": "contradiction_requires_recheck", "enforced": True},
        ],
        "world_version": req.world_version,
        "evidence_state": {"status": evidence_status, "contradictions": contradictions},
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
    return {k: record[k] for k in ("decision", "decision_id", "request_id", "tenant_id", "actor_id", "session_id", "risk_assessment", "policy_checks", "evidence", "trace_id", "created_at", "expires_at", "nonce", "action_hash", "policy_version", "policy_hash", "decision_signature", "evidence_hash", "world_version")} | {"reason": policy_checks[0]["reason"]}




from self_audit import Evidence as SelfAuditEvidence, SelfAuditRequest, audit as self_audit


class SelfAuditEvidenceItem(BaseModel):
    source: str
    verified: bool = False
    supports: list[str] = Field(default_factory=list)
    note: str | None = None


class SelfAuditActionRequest(BaseModel):
    tenant_id: str
    actor_id: str
    session_id: str
    action: str
    target: str | None = None
    claim: str | None = None
    evidence: list[SelfAuditEvidenceItem] = Field(default_factory=list)
    external_side_effect: bool = False
    mutating: bool = False
    requires_model_internal_access: bool = False


@app.post("/v1/self-audit")
def self_audit_endpoint(req: SelfAuditActionRequest, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, req.tenant_id)
    result = self_audit(SelfAuditRequest(
        actor_id=req.actor_id,
        session_id=req.session_id,
        action=req.action,
        target=req.target,
        claim=req.claim,
        evidence=tuple(SelfAuditEvidence(
            source=item.source,
            verified=item.verified,
            supports=tuple(item.supports),
            note=item.note,
        ) for item in req.evidence),
        external_side_effect=req.external_side_effect,
        mutating=req.mutating,
        requires_model_internal_access=req.requires_model_internal_access,
    ))
    return {
        "decision": result.decision.value,
        "executable": result.executable,
        "reasons": list(result.reasons),
        "evidence_coverage": result.evidence_coverage,
        "claim_evidence_gap": result.claim_evidence_gap,
        "action_hash": result.action_hash,
    }


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
    if ENVIRONMENT == "production":
        if not APPROVAL_SECRET:
            raise HTTPException(503, "production_approval_secret_not_configured")
        if not verify_approval_signature(approval):
            raise HTTPException(401, "approval_signature_invalid")
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
    if outcome.nonce != record["nonce"]:
        raise HTTPException(409, "execution_nonce_mismatch")
    current_state = get_current_snapshot()
    if record.get("world_version") is not None:
        if outcome.world_version != record.get("world_version"):
            raise HTTPException(409, "execution_world_version_mismatch")
        if current_state is None or current_state["world_version"] != record.get("world_version"):
            raise HTTPException(409, "execution_world_state_changed")
    if record.get("evidence_state", {}).get("contradictions"):
        raise HTTPException(409, "execution_blocked_by_evidence_contradiction")
    if record.get("evidence_state", {}).get("status") == "BLOCK":
        raise HTTPException(409, "execution_blocked_by_evidence_state")
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
    authority_secret = os.getenv("ACTION_GATE_AUTHORITY_SECRET") or current_secret()
    if not authority_secret:
        raise HTTPException(503, "execution_authority_not_configured")
    if not authority_secret:
        raise HTTPException(503, "execution_authority_not_configured")
    remaining_ttl = max(1, int((datetime.fromisoformat(record["expires_at"]) - datetime.now(timezone.utc)).total_seconds()))
    authority = issue_authority(
        secret=authority_secret.encode(),
        decision_id=decision_id,
        tenant_id=record["tenant_id"],
        action=record["normalized_action"],
        policy=record["policy_snapshot"],
        decision=record["decision"],
        ttl_seconds=remaining_ttl,
        now=int(time.time()),
        nonce=record["nonce"],
    )
    record["execution_authority"] = authority.token()
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
    if record.get("request", {}).get("session_id") is not None and outcome.session_id != record["request"].get("session_id"):
        raise HTTPException(409, "execution_session_binding_mismatch")
    if outcome.nonce != record["nonce"]:
        raise HTTPException(409, "execution_nonce_mismatch")
    current_state = get_current_snapshot()
    if record.get("world_version") is not None:
        if outcome.world_version != record.get("world_version"):
            raise HTTPException(409, "execution_world_version_mismatch")
        if current_state is None or current_state["world_version"] != record.get("world_version"):
            raise HTTPException(409, "execution_world_state_changed")
    if record.get("evidence_state", {}).get("contradictions"):
        raise HTTPException(409, "execution_blocked_by_evidence_contradiction")
    if record.get("evidence_state", {}).get("status") == "BLOCK":
        raise HTTPException(409, "execution_blocked_by_evidence_state")
    if record["approval"] and record["approval"].get("approved") and datetime.fromisoformat(record["approval"]["expires_at"]) <= datetime.now(timezone.utc):
        raise HTTPException(403, "approval_expired")
    if record.get("execution_started_at") is None:
        raise HTTPException(409, "execution_not_reserved")
    if not record.get("execution_authority"):
        raise HTTPException(409, "execution_authority_missing")
    if record.get("reconciliation") is not None or record.get("execution", {}).get("status") == "RECONCILED":
        raise HTTPException(409, "execution_already_reconciled")
    consumed_at = now()
    try:
        finalized = finalize_execution(record, outcome.nonce, consumed_at, digest, canonical, now, outcome.outcome)
    except Exception as exc:
        raise HTTPException(503, "execution_finalization_store_unavailable") from exc
    if not finalized:
        raise HTTPException(409, "decision_nonce_already_consumed_or_execution_not_reserved")
    return finalized


@app.post("/v1/action/{decision_id}/execution/reconcile")
def execution_reconcile(decision_id: str, outcome: ReconciliationOutcome, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, outcome.tenant_id)
    record = load(decision_id, outcome.tenant_id)
    ensure_live(record)
    if record["decision"] != "ALLOW":
        raise HTTPException(403, "execution_not_permitted_by_gate")
    if outcome.action_hash != record["action_hash"]:
        raise HTTPException(409, "reconciliation_action_binding_mismatch")
    if outcome.nonce != record["nonce"]:
        raise HTTPException(409, "reconciliation_nonce_mismatch")
    if record.get("execution_started_at") is None:
        raise HTTPException(409, "execution_not_reserved")
    if record.get("consumed_at") is not None:
        raise HTTPException(409, "execution_already_finalized")
    if record.get("reconciliation") is not None:
        raise HTTPException(409, "execution_already_reconciled")
    if outcome.resolution not in {"CONFIRMED_FILLED", "CONFIRMED_NOT_EXECUTED"}:
        raise HTTPException(422, "invalid_reconciliation_resolution")
    resolved_at = now()
    try:
        finalized = reconcile_execution(record, outcome.nonce, resolved_at, outcome.resolution, outcome.outcome, digest, canonical, now)
    except Exception as exc:
        raise HTTPException(503, "execution_reconciliation_store_unavailable") from exc
    if not finalized:
        raise HTTPException(409, "execution_reconciliation_conflict")
    return finalized


@app.get("/v1/replay/{decision_id}")
def replay(decision_id: str, tenant_id: str, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, tenant_id)
    record = load(decision_id, tenant_id)
    snapshot = record["policy_snapshot"]
    schema_version = record.get("schema_version", "action-gate-evidence-3.0")
    raw_request = dict(record["request"])
    stored_signal = None
    if schema_version == "action-gate-evidence-3.1":
        stored_signal = PreExecutionSignal.model_validate(record["pre_execution_signal"])
        raw_request.pop("pre_execution_signal", None)
    elif schema_version == "action-gate-evidence-3.0":
        legacy_signal_data = raw_request.pop("pre_execution_signal", None)
        if legacy_signal_data is not None:
            stored_signal = PreExecutionSignal.model_validate(legacy_signal_data)
    else:
        raise HTTPException(500, "unsupported_decision_schema_version")
    req = ActionRequest.model_validate(raw_request)
    policy_hash_match = digest(snapshot) == record["policy_hash"]
    replay_evidence_status, replay_evidence, replay_contradictions = evidence_gate(record.get("evidence", []))
    req.evidence = replay_evidence
    if schema_version == "action-gate-evidence-3.1":
        action_hash_match = digest(normalized_action(req, stored_signal)) == record["action_hash"]
    else:
        action_hash_match = digest(legacy_normalized_action(req, stored_signal)) == record["action_hash"]
    risk, _ = evaluate_risk(req, snapshot)
    if schema_version == "action-gate-evidence-3.1":
        decision, checks = decide(req, risk, stored_signal, snapshot)
    else:
        decision, checks = decide_legacy(req, risk, snapshot, stored_signal)
    original = record["decision"]
    expected = "ASK" if record["approval"] is not None and original in {"ALLOW", "DENY"} else original
    match = decision == expected and policy_hash_match and action_hash_match and not replay_contradictions
    return {"decision_id": decision_id, "trace_id": record["trace_id"], "replayed_decision": decision, "recorded_preapproval_decision": expected, "match": match, "risk": risk, "policy_checks": checks, "policy_hash": record["policy_hash"], "policy_hash_match": policy_hash_match, "action_hash": record["action_hash"], "action_hash_match": action_hash_match, "evidence_hash": record["evidence_hash"], "audit_event_hash": record.get("audit_event_hash"), "evidence_state": replay_evidence_status, "contradictions": replay_contradictions}


@app.get("/v1/evidence/{decision_id}")
def evidence(decision_id: str, tenant_id: str, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    enforce_rate_limit(authorization, tenant_id)
    return load(decision_id, tenant_id)
