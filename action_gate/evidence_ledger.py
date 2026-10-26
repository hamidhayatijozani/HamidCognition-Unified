from __future__ import annotations

import copy
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
        self._event_ids: set[str] = set()

    @staticmethod
    def _hash(event_id: str, event_type: str, trace_id: str, payload: dict[str, Any], previous_hash: str) -> str:
        raw = json.dumps(
            {
                "event_id": event_id,
                "event_type": event_type,
                "trace_id": trace_id,
                "payload": payload,
                "previous_hash": previous_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def append(self, event_id: str, event_type: str, trace_id: str, payload: dict[str, Any]) -> LedgerEvent:
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id_must_be_non_empty_string")
        if event_id in self._event_ids:
            raise ValueError("duplicate_event_id")
        # Snapshot nested caller-owned values before hashing. A shallow dict copy
        # lets post-append mutations silently change the evidence being verified.
        payload_snapshot = copy.deepcopy(payload)
        previous_hash = self._events[-1].event_hash if self._events else "GENESIS"
        event_hash = self._hash(event_id, event_type, trace_id, payload_snapshot, previous_hash)
        event = LedgerEvent(event_id, event_type, trace_id, payload_snapshot, previous_hash, event_hash)
        self._events.append(event)
        self._event_ids.add(event_id)
        return event

    def events(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)

    def verify_chain(self) -> bool:
        previous = "GENESIS"
        seen: set[str] = set()
        for event in self._events:
            if event.event_id in seen:
                return False
            try:
                expected = self._hash(event.event_id, event.event_type, event.trace_id, event.payload, previous)
            except (TypeError, ValueError):
                return False
            if event.previous_hash != previous or event.event_hash != expected:
                return False
            seen.add(event.event_id)
            previous = event.event_hash
        return seen == self._event_ids

    def delete(self, event_id: str) -> None:
        raise PermissionError("evidence_ledger_is_append_only")

    def update(self, event_id: str, payload: dict[str, Any]) -> None:
        raise PermissionError("evidence_ledger_is_append_only")
