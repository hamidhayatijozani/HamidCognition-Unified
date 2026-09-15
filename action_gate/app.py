from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

APP_VERSION = "0.2.0-mvp"
DB_PATH = os.getenv("ACTION_GATE_DB", "action_gate.db")
API_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
POLICY_SNAPSHOT = {
    "policy_version": "builtin-v1",
    "high_risk": ["delete_file", "delete_customer", "delete_database", "transfer_funds", "transfer_money"],
    "external": ["send_email", "send_external_email", "http_post_external"],
    "critical": ["transfer_funds", "transfer_money"],
    "rules": ["critical financial action -> SANDBOX", "critical destructive production action -> DENY", "high-risk destructive or external communication -> ASK", "otherwise -> ALLOW"],
}
POLICY_HASH = hashlib.sha256(json.dumps(POLICY_SNAPSHOT, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
app = FastAPI(title="HamidCognition Action Gate", version=APP_VERSION)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def require_auth(authorization: str | None) -> None:
    if API_TOKEN is not None and authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(401, "invalid_action_gate_credentials")


def db():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS records (decision_id TEXT PRIMARY KEY, trace_id TEXT, record TEXT NOT NULL)")
    return con


class ActionRequest(BaseModel):
    request_id: str | None = None
    agent_id: str
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
    return {"action": req.action.lower(), "target": req.target, "parameters": req.parameters}


def save(record: dict[str, Any]) -> None:
    con = db()
    con.execute("INSERT OR REPLACE INTO records VALUES (?,?,?)", (record["decision_id"], record["trace_id"], canonical(record)))
    con.commit(); con.close()


def load(decision_id: str):
    con = db(); row = con.execute("SELECT record FROM records WHERE decision_id=?", (decision_id,)).fetchone(); con.close()
    if not row: raise HTTPException(404, "decision_not_found")
    return json.loads(row[0])


@app.get("/health")
def health():
    return {"status": "ok", "product": "HamidCognition Action Gate", "version": APP_VERSION, "policy_hash": POLICY_HASH}


@app.post("/v1/action/evaluate")
def evaluate(req: ActionRequest, authorization: str | None = Header(default=None)):
    require_auth(authorization)
    request_id = req.request_id or f"req_{uuid.uuid4().hex}"
    decision_id = f"dec_{uuid.uuid4().hex}"; trace_id = f"trace_{uuid.uuid4().hex}"
    risk, risk_reasons = evaluate_risk(req); decision, policy_checks = decide(req, risk); normalized = normalized_action(req)
    record = {"schema_version": "action-gate-evidence-1.1", "product_version": APP_VERSION, "decision_id": decision_id, "trace_id": trace_id, "request_id": request_id, "request": req.model_dump(), "identity": {"agent_id": req.agent_id}, "normalized_action": normalized, "action_hash": digest(normalized), "policy_version": POLICY_SNAPSHOT["policy_version"], "policy_snapshot": POLICY_SNAPSHOT, "policy_hash": POLICY_HASH, "risk_assessment": {"level": risk, "reasons": risk_reasons, "agent_risk_hint": req.risk_hint}, "evidence": req.evidence, "decision": decision, "policy_checks": policy_checks, "approval": None, "execution": None, "outcome": None, "timestamp": now()}
    record["evidence_hash"] = digest(record); save(record)
    return {k: record[k] for k in ("decision", "decision_id", "request_id", "risk_assessment", "policy_checks", "evidence", "trace_id", "timestamp", "evidence_hash", "action_hash", "policy_version", "policy_hash")} | {"reason": policy_checks[0]["reason"]}


@app.post("/v1/action/{decision_id}/approve")
def approve(decision_id: str, approval: Approval, authorization: str | None = Header(default=None)):
    require_auth(authorization); record = load(decision_id)
    if record["decision"] != "ASK": raise HTTPException(409, "decision_is_not_awaiting_approval")
    record["approval"] = {**approval.model_dump(), "timestamp": now(), "action_hash": record["action_hash"]}
    record["decision"] = "ALLOW" if approval.approved else "DENY"; record["evidence_hash"] = digest(record); save(record); return record


@app.post("/v1/action/{decision_id}/execution")
def execution(decision_id: str, outcome: dict[str, Any], authorization: str | None = Header(default=None)):
    require_auth(authorization); record = load(decision_id)
    if record["decision"] not in {"ALLOW", "SANDBOX"}: raise HTTPException(403, "execution_not_permitted_by_gate")
    record["execution"] = {"timestamp": now(), "status": "EXECUTED", "action_hash": record["action_hash"]}; record["outcome"] = outcome; record["evidence_hash"] = digest(record); save(record); return record


@app.get("/v1/replay/{decision_id}")
def replay(decision_id: str, authorization: str | None = Header(default=None)):
    require_auth(authorization); record = load(decision_id); req = ActionRequest.model_validate(record["request"]); snapshot = record["policy_snapshot"]
    policy_hash_match = digest(snapshot) == record["policy_hash"]; action_hash_match = digest(normalized_action(req)) == record["action_hash"]
    risk, _ = evaluate_risk(req, snapshot); decision, checks = decide(req, risk, snapshot); original = record["decision"]
    expected = "ASK" if record["approval"] is not None and original in {"ALLOW", "DENY"} else original
    match = decision == expected and policy_hash_match and action_hash_match
    return {"decision_id": decision_id, "trace_id": record["trace_id"], "replayed_decision": decision, "recorded_preapproval_decision": expected, "match": match, "risk": risk, "policy_checks": checks, "policy_hash": record["policy_hash"], "policy_hash_match": policy_hash_match, "action_hash": record["action_hash"], "action_hash_match": action_hash_match, "evidence_hash": record["evidence_hash"]}


@app.get("/v1/evidence/{decision_id}")
def evidence(decision_id: str, authorization: str | None = Header(default=None)):
    require_auth(authorization); return load(decision_id)
