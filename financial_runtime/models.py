from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

class DecisionState(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ASK = "ASK"
    SANDBOX = "SANDBOX"
    DEFER = "DEFER"

class ExecutionState(str, Enum):
    PLANNED = "PLANNED"
    AUTHORIZED = "AUTHORIZED"
    DISPATCHED = "DISPATCHED"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"
    VERIFIED = "VERIFIED"

@dataclass(frozen=True)
class FinancialEvent:
    event_id: str
    source: str
    occurred_at: str
    amount: Decimal
    currency: str
    reference: str | None = None
    account_ref: str | None = None
    counterparty: str | None = None
    description: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class MatchCandidate:
    source_event_id: str
    target_event_id: str
    score: Decimal
    reasons: tuple[str, ...] = ()

@dataclass(frozen=True)
class ExecutionRecord:
    operation_id: str
    operation_hash: str
    state: ExecutionState
    decision: DecisionState
    evidence_hash: str
    destination: str
