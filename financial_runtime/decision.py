from __future__ import annotations
from .models import DecisionState, MatchCandidate

def decide(candidates: tuple[MatchCandidate, ...], *, evidence_complete: bool, already_executed: bool, policy_allows: bool) -> tuple[DecisionState, tuple[str, ...]]:
    if already_executed:
        return DecisionState.DENY, ("operation_already_executed",)
    if not evidence_complete:
        return DecisionState.DEFER, ("required_evidence_missing",)
    if not policy_allows:
        return DecisionState.DENY, ("policy_denied",)
    if not candidates:
        return DecisionState.ASK, ("no_match_candidate",)
    if len(candidates) == 1 and candidates[0].score == 1:
        return DecisionState.ALLOW, ("single_exact_candidate",)
    return DecisionState.ASK, ("ambiguous_match_requires_review",)
