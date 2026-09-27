from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from evidence_ledger import LedgerEvent


@dataclass(frozen=True)
class ForensicSignal:
    signal_type: str
    severity: str
    trace_id: str
    detail: str


class PostExecutionForensics:
    """Deterministic first-line analysis over the execution trail."""

    def analyze(self, events: Iterable[LedgerEvent]) -> tuple[ForensicSignal, ...]:
        events = tuple(events)
        signals: list[ForensicSignal] = []
        actions_by_trace: dict[str, list[str]] = {}
        authorities_by_trace: dict[str, set[str]] = {}
        policy_counts: Counter[str] = Counter()
        for event in events:
            payload = event.payload
            if event.event_type != "EXECUTION":
                continue
            trace = event.trace_id
            actions_by_trace.setdefault(trace, []).append(str(payload.get("action")))
            policy_counts[str(payload.get("policy_id"))] += 1
            authorities_by_trace.setdefault(trace, set()).add(str(payload.get("authority_id")))
        for trace, actions in actions_by_trace.items():
            if len(actions) >= 3 and len(set(actions[-3:])) == 1:
                signals.append(ForensicSignal("repeated_action_pattern", "MEDIUM", trace,
                                              "same action executed three times in the recent trace"))
            if len(authorities_by_trace.get(trace, set())) > 1:
                signals.append(ForensicSignal("authority_churn", "MEDIUM", trace,
                                              "same trace used multiple authority identities"))
        for policy_id, count in policy_counts.items():
            if count >= 10:
                signals.append(ForensicSignal("policy_usage_spike", "LOW", "*",
                                              f"policy {policy_id} observed {count} execution events"))
        return tuple(signals)
