from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_VERSION = "0.1.0-mvp"
DECISIONS = {"ALLOW", "DENY", "ASK", "SANDBOX", "DEFER"}
DB_PATH = os.getenv("ACTION_GATE_DB", "action_gate.db")

app = FastAPI(title="HamidCognition Action Gate", version=APP_VERSION)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


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


HIGH_RISK = {"delete_file", "delete_customer", "delete_database", "transfer_funds", "transfer_money"}
EXTERNAL = {"send_email", "send_external_email", "http_post_external"}
CRITICAL = {"transfer_funds", "transfer_money"}


def evaluate_risk(req: ActionRequest) -> tuple[str, list[str]]:
    a = req.action.lower()
    reasons: list[str] = []
    if a in CRITICAL:
        return "CRITICAL", ["financial_transfer_is_inherently_high_risk"]
    if a in HIGH_RISK:
        reasons.append("destructive_action")
        if req.target and ("production" in req.target.lower() or "prod" in req.target.lower()):
            reasons.append("production_target")
            return "CRITICAL", reasons
        return "HIGH", reasons
    if a in EXTERNAL:
        return "HIGH", ["external_communication"]
    return "LOW", ["no_intrinsic_high_risk_rule_matched"]


def decide(req: ActionRequest, risk: str) -> tuple[str, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    a = req.action.lower()
    if a in CRITICAL:
        checks.append({"policy": "financial-transfer", "result": "SANDBOX", "reason": "critical_action_requires_containment_or_human_review"})
        return "SANDBOX", checks
    if a in HIGH_RISK and risk == "CRITICAL":
        checks.append({"policy": "production-destructive-action", "result": "DENY", "reason": "destructive_production_action_blocked"})
        return "DENY", checks
    if a in HIGH_RISK or a in EXTERNAL:
        checks.append({"policy": "sensitive-action-approval", "result": "ASK", "reason": "human_approval_required"})
        return "ASK", checks
    checks.append({"policy": "default", "result": "ALLOW", "reason": "no_blocking_policy_matched"})
    return "ALLOW", checks


def save(record: dict[str, Any]) -> None:
    con = db()
    con.execute("INSERT OR REPLACE INTO records VALUES (?,?,?)", (record["decision_id"], record["trace_id"], canonical(record)))
    con.commit()
    con.close()


def load(decision_id: str) -> dict[str, Any]:
    con = db()
    row = con.execute("SELECT record FROM records WHERE decision_id=?", (decision_id,)).fetchone()
    con.close()
    if not row:
        raise HTTPException(404, "decision_not_found")
    return json.loads(row[0])


@app.get("/health")
def health():
    return {"status": "ok", "product": "HamidCognition Action Gate", "version": APP_VERSION}


@app.post("/v1/action/evaluate")
def evaluate(req: ActionRequest):
    request_id = req.request_id or f"req_{uuid.uuid4().hex}"
    decision_id = f"dec_{uuid.uuid4().hex}"
    trace_id = f"trace_{uuid.uuid4().hex}"
    risk, risk_reasons = evaluate_risk(req)
    decision, policy_checks = decide(req, risk)
    normalized = {"action": req.action.lower(), "target": req.target, "parameters": req.parameters}
    record = {
        "schema_version": "action-gate-evidence-1.0",
        "product_version": APP_VERSION,
        "decision_id": decision_id,
        "trace_id": trace_id,
        "request_id": request_id,
        "request": req.model_dump(),
        "identity": {"agent_id": req.agent_id},
        "normalized_action": normalized,
        "policy_version": "builtin-v1",
        "risk_assessment": {"level": risk, "reasons": risk_reasons, "agent_risk_hint": req.risk_hint},
        "evidence": req.evidence,
        "decision": decision,
        "policy_checks": policy_checks,
        "approval": None,
        "execution": None,
        "outcome": None,
        "timestamp": now(),
    }
    record["evidence_hash"] = digest(record)
    save(record)
    return {k: record[k] for k in ("decision", "decision_id", "request_id", "risk_assessment", "policy_checks", "evidence", "trace_id", "timestamp", "evidence_hash")} | {"reason": policy_checks[0]["reason"]}


@app.post("/v1/action/{decision_id}/approve")
def approve(decision_id: str, approval: Approval):
    record = load(decision_id)
    if record["decision"] != "ASK":
        raise HTTPException(409, "decision_is_not_awaiting_approval")
    record["approval"] = {**approval.model_dump(), "timestamp": now()}
    record["decision"] = "ALLOW" if approval.approved else "DENY"
    record["evidence_hash"] = digest(record)
    save(record)
    return record


@app.post("/v1/action/{decision_id}/execution")
def execution(decision_id: str, outcome: dict[str, Any]):
    record = load(decision_id)
    if record["decision"] not in {"ALLOW", "SANDBOX"}:
        raise HTTPException(403, "execution_not_permitted_by_gate")
    record["execution"] = {"timestamp": now(), "status": "EXECUTED"}
    record["outcome"] = outcome
    record["evidence_hash"] = digest(record)
    save(record)
    return record


@app.get("/v1/replay/{decision_id}")
def replay(decision_id: str):
    record = load(decision_id)
    req = ActionRequest.model_validate(record["request"])
    risk, reasons = evaluate_risk(req)
    decision, checks = decide(req, risk)
    original = record["decision"]
    # ASK may have become ALLOW/DENY after approval; replay validates the pre-approval gate decision.
    expected = "ASK" if record["approval"] is not None and original in {"ALLOW", "DENY"} else original
    match = decision == expected
    return {"decision_id": decision_id, "trace_id": record["trace_id"], "replayed_decision": decision, "recorded_preapproval_decision": expected, "match": match, "risk": risk, "policy_checks": checks, "evidence_hash": record["evidence_hash"]}


@app.get("/v1/evidence/{decision_id}")
def evidence(decision_id: str):
    return load(decision_id)
