from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LedgerEvent:
    event_id: str
    event_type: str
    trace_id: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str


class EvidenceLedger:
    """Append-only hash-chained evidence contract."""

    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []

    @staticmethod
    def _hash(event_id: str, event_type: str, trace_id: str, payload: dict[str, Any], previous_hash: str) -> str:
        raw = json.dumps({"event_id": event_id, "event_type": event_type, "trace_id": trace_id,
                          "payload": payload, "previous_hash": previous_hash},
                         sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()

    def append(self, event_id: str, event_type: str, trace_id: str, payload: dict[str, Any]) -> LedgerEvent:
        previous_hash = self._events[-1].event_hash if self._events else "GENESIS"
        event_hash = self._hash(event_id, event_type, trace_id, payload, previous_hash)
        event = LedgerEvent(event_id, event_type, trace_id, dict(payload), previous_hash, event_hash)
        self._events.append(event)
        return event

    def events(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)

    def verify_chain(self) -> bool:
        previous = "GENESIS"
        for event in self._events:
            expected = self._hash(event.event_id, event.event_type, event.trace_id, event.payload, previous)
            if event.previous_hash != previous or event.event_hash != expected:
                return False
            previous = event.event_hash
        return True

    def delete(self, event_id: str) -> None:
        raise PermissionError("evidence_ledger_is_append_only")

    def update(self, event_id: str, payload: dict[str, Any]) -> None:
        raise PermissionError("evidence_ledger_is_append_only")
