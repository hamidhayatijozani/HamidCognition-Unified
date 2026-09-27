from __future__ import annotations
from typing import Any, Protocol
from .decision import decide
from .evidence import build_evidence
from .idempotency import IdempotencyVault
from .models import DecisionState, ExecutionRecord, ExecutionState, FinancialEvent, MatchCandidate

class DestinationAdapter(Protocol):
    name: str
    def execute(self, event: FinancialEvent, candidate: MatchCandidate) -> dict[str, Any]: ...
    def verify(self, execution: dict[str, Any]) -> dict[str, Any]: ...

class ControlledFinancialRuntime:
    def __init__(self, vault: IdempotencyVault | None = None) -> None:
        self.vault = vault or IdempotencyVault()

    def authorize(self, *, operation_id: str, source: FinancialEvent, candidate: MatchCandidate | None, evidence_complete: bool, policy_allows: bool, destination: str):
        payload = {"operation_id": operation_id, "source_event_id": source.event_id, "candidate_event_id": candidate.target_event_id if candidate else None, "destination": destination}
        op_hash, fresh = self.vault.reserve(payload)
        decision, reasons = decide((candidate,) if candidate else (), evidence_complete=evidence_complete, already_executed=not fresh, policy_allows=policy_allows)
        self.vault.update(op_hash, DecisionState.ALLOW.value if decision == DecisionState.ALLOW else decision.value)
        return decision, reasons, op_hash

    def execute(self, *, operation_id: str, source: FinancialEvent, candidate: MatchCandidate, destination: DestinationAdapter, evidence_complete: bool = True, policy_allows: bool = True) -> ExecutionRecord:
        decision, _, op_hash = self.authorize(operation_id=operation_id, source=source, candidate=candidate, evidence_complete=evidence_complete, policy_allows=policy_allows, destination=destination.name)
        if decision != DecisionState.ALLOW:
            evidence = build_evidence(operation_id=operation_id, source_events=[source.raw], candidates=[{"target_event_id": candidate.target_event_id, "score": str(candidate.score), "reasons": candidate.reasons}], decision=decision.value, execution_state=ExecutionState.FAILED.value, destination=destination.name)
            return ExecutionRecord(operation_id, op_hash, ExecutionState.FAILED, decision, evidence["evidence_hash"], destination.name)
        self.vault.update(op_hash, ExecutionState.DISPATCHED.value)
        try:
            result = destination.execute(source, candidate)
        except Exception as exc:
            self.vault.update(op_hash, ExecutionState.UNKNOWN.value)
            evidence = build_evidence(operation_id=operation_id, source_events=[source.raw], candidates=[{"target_event_id": candidate.target_event_id, "score": str(candidate.score), "reasons": candidate.reasons}], decision=decision.value, execution_state=ExecutionState.UNKNOWN.value, destination=destination.name, verification={"status": "unknown", "error_type": type(exc).__name__})
            return ExecutionRecord(operation_id, op_hash, ExecutionState.UNKNOWN, decision, evidence["evidence_hash"], destination.name)
        verification = destination.verify(result)
        state = ExecutionState.VERIFIED if bool(verification.get("verified")) else ExecutionState.UNKNOWN
        self.vault.update(op_hash, state.value)
        evidence = build_evidence(operation_id=operation_id, source_events=[source.raw], candidates=[{"target_event_id": candidate.target_event_id, "score": str(candidate.score), "reasons": candidate.reasons}], decision=decision.value, execution_state=state.value, destination=destination.name, verification=verification)
        return ExecutionRecord(operation_id, op_hash, state, decision, evidence["evidence_hash"], destination.name)
