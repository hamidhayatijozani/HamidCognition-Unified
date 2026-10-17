"""Tamper-detection tests for the in-memory evidence-ledger contract.

This tests hash-chain integrity only. It does not claim durable or externally
anchored production-ledger protection.
"""
from evidence_ledger import EvidenceLedger


def test_payload_mutation_is_detected_by_chain_verification():
    ledger = EvidenceLedger()
    ledger.append("event-1", "DECISION", "trace-1", {"decision": "ALLOW"})
    ledger.append("event-2", "EXECUTION", "trace-1", {"result": "accepted"})
    assert ledger.verify_chain() is True

    # Simulate an attacker or faulty storage layer modifying an event payload
    # without recomputing its hash and every downstream link.
    ledger.events()[0].payload["decision"] = "DENY"

    assert ledger.verify_chain() is False


def test_previous_hash_mutation_is_detected():
    ledger = EvidenceLedger()
    ledger.append("event-1", "DECISION", "trace-1", {"decision": "ALLOW"})
    ledger.append("event-2", "EXECUTION", "trace-1", {"result": "accepted"})
    second = ledger._events[1]
    ledger._events[1] = second.__class__(
        event_id=second.event_id,
        event_type=second.event_type,
        trace_id=second.trace_id,
        payload=second.payload,
        previous_hash="0" * 64,
        event_hash=second.event_hash,
    )

    assert ledger.verify_chain() is False
