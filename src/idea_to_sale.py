"""Deterministic Idea-to-Sale commercialization engine."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from hashlib import sha256
import json
from typing import Any

class Status(str, Enum):
    BLOCKED = "BLOCKED"
    VERIFIED = "VERIFIED"

@dataclass(frozen=True)
class Gate:
    name: str
    status: Status
    reason: str

@dataclass(frozen=True)
class CommercialPlan:
    idea_id: str
    canonical_idea: str
    customer_problem: str
    target_buyer: str
    product_boundary: str
    evidence_required: tuple[str, ...]
    sales_assets: tuple[str, ...]
    gates: tuple[Gate, ...]
    next_action: str
    truth_boundary: str
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)

def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()

def plan_hash(plan: CommercialPlan) -> str:
    return sha256(canonical_bytes(asdict(plan))).hexdigest()

def build_plan(idea: str, *, customer_problem: str = "", target_buyer: str = "",
               product_boundary: str = "", evidence: list[str] | None = None,
               sales_assets: list[str] | None = None, validation_verified: bool = False,
               pricing_defined: bool = False, payment_path_configured: bool = False) -> CommercialPlan:
    if not isinstance(idea, str) or not idea.strip():
        raise ValueError("idea_required")
    evidence = evidence or []
    sales_assets = sales_assets or []
    def gate(name, ok, yes, no):
        return Gate(name, Status.VERIFIED if ok else Status.BLOCKED, yes if ok else no)
    gates = (
        gate("problem_defined", bool(customer_problem.strip()), "customer problem is explicit", "customer_problem_missing"),
        gate("buyer_defined", bool(target_buyer.strip()), "target buyer is explicit", "target_buyer_missing"),
        gate("product_boundary_defined", bool(product_boundary.strip()), "product boundary is explicit", "product_boundary_missing"),
        gate("evidence", validation_verified and bool(evidence), "validation evidence supplied", "verified_evidence_missing"),
        gate("pricing", pricing_defined, "pricing defined", "pricing_missing"),
        gate("sales_assets", bool(sales_assets), "sales assets supplied", "sales_assets_missing"),
        gate("payment_path", payment_path_configured, "payment path configured", "payment_path_not_configured"),
    )
    blocked = [g.name for g in gates if g.status == Status.BLOCKED]
    return CommercialPlan(
        idea_id=sha256(idea.strip().encode()).hexdigest()[:16],
        canonical_idea=idea.strip(), customer_problem=customer_problem.strip(),
        target_buyer=target_buyer.strip(), product_boundary=product_boundary.strip(),
        evidence_required=tuple(evidence), sales_assets=tuple(sales_assets), gates=gates,
        next_action="HUMAN_APPROVAL" if not blocked else f"RESOLVE:{blocked[0]}",
        truth_boundary="No customer, revenue, payment, validation, or performance claim may be VERIFIED without evidence.",
    )

def ready_for_sale(plan: CommercialPlan) -> bool:
    return all(g.status != Status.BLOCKED for g in plan.gates)

def audit_event(plan: CommercialPlan) -> dict[str, Any]:
    return {"event":"commercial_plan","ideaId":plan.idea_id,"planHash":plan_hash(plan),
            "readyForSale":ready_for_sale(plan),"nextAction":plan.next_action,
            "gates":[asdict(g) for g in plan.gates]}

if __name__ == "__main__":
    import sys
    payload = json.load(sys.stdin)
    print(json.dumps(audit_event(build_plan(**payload)), ensure_ascii=False, sort_keys=True))