"""Deterministic self-audit harness for applying Action Gate principles to a proposed model action or claim.

This module does not execute tools and does not alter model internals. It evaluates a
proposed action against explicit evidence, identity/session binding, and claim scope.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import hashlib
import json


class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ASK = "ASK"
    SANDBOX = "SANDBOX"
    DEFER = "DEFER"


@dataclass(frozen=True)
class Evidence:
    source: str
    verified: bool
    supports: tuple[str, ...] = ()
    note: str | None = None


@dataclass(frozen=True)
class SelfAuditRequest:
    actor_id: str
    session_id: str
    action: str
    target: str | None = None
    claim: str | None = None
    evidence: tuple[Evidence, ...] = ()
    external_side_effect: bool = False
    mutating: bool = False
    requires_model_internal_access: bool = False
    requested_decision: GateDecision | None = None


@dataclass(frozen=True)
class SelfAuditResult:
    decision: GateDecision
    executable: bool
    reasons: tuple[str, ...]
    evidence_coverage: float
    claim_evidence_gap: float
    action_hash: str


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def audit(request: SelfAuditRequest) -> SelfAuditResult:
    reasons: list[str] = []
    evidence = request.evidence
    verified = [item for item in evidence if item.verified]

    if not request.actor_id:
        return SelfAuditResult(
            GateDecision.DENY, False, ("actor_identity_missing",), 0.0, 1.0,
            _digest(request),
        )
    if not request.session_id:
        return SelfAuditResult(
            GateDecision.DENY, False, ("session_binding_missing",), 0.0, 1.0,
            _digest(request),
        )

    evidence_coverage = len(verified) / len(evidence) if evidence else 0.0
    claim_evidence_gap = 0.0 if verified else 1.0

    if request.claim:
        claim_tokens = set(request.claim.lower().split())
        supporting = 0
        for item in verified:
            if any(token in claim_tokens for token in item.supports):
                supporting += 1
        if verified:
            claim_evidence_gap = max(0.0, 1.0 - supporting / len(verified))

    if request.requires_model_internal_access:
        reasons.append("model_internal_state_not_observable")
        return SelfAuditResult(
            GateDecision.DENY, False, tuple(reasons), evidence_coverage,
            max(claim_evidence_gap, 1.0), _digest(request),
        )

    if not verified:
        reasons.append("no_verified_evidence")
        if request.external_side_effect or request.mutating:
            return SelfAuditResult(
                GateDecision.ASK, False, tuple(reasons + ["human_review_required"]),
                evidence_coverage, 1.0, _digest(request),
            )
        return SelfAuditResult(
            GateDecision.DEFER, False, tuple(reasons + ["claim_or_action_not_verified"]),
            evidence_coverage, 1.0, _digest(request),
        )

    if request.claim and claim_evidence_gap >= 1.0:
        reasons.append("claim_evidence_gap")
        return SelfAuditResult(
            GateDecision.DENY, False, tuple(reasons),
            evidence_coverage, claim_evidence_gap, _digest(request),
        )

    if request.external_side_effect or request.mutating:
        reasons.append("side_effect_requires_explicit_execution_boundary")
        return SelfAuditResult(
            GateDecision.ASK, False, tuple(reasons + ["approval_or_external_gate_required"]),
            evidence_coverage, claim_evidence_gap, _digest(request),
        )

    reasons.append("bounded_action_or_claim_supported_by_verified_evidence")
    return SelfAuditResult(
        GateDecision.ALLOW, True, tuple(reasons),
        evidence_coverage, claim_evidence_gap, _digest(request),
    )
