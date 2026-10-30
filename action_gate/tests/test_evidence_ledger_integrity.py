import pytest

from action_gate.evidence_ledger import EvidenceLedger


def test_duplicate_event_id_is_rejected():
    ledger = EvidenceLedger()
    ledger.append("event-1", "DECISION", "trace-1", {"decision": "ALLOW"})
    with pytest.raises(ValueError, match="duplicate_event_id"):
        ledger.append("event-1", "EXECUTION", "trace-1", {"result": "accepted"})


def test_nested_payload_and_returned_events_are_isolated_copies():
    ledger = EvidenceLedger()
    payload = {"nested": {"decision": "ALLOW"}}
    returned = ledger.append("event-1", "DECISION", "trace-1", payload)

    payload["nested"]["decision"] = "DENY"
    returned.payload["nested"]["decision"] = "SANDBOX"

    assert ledger.events()[0].payload["nested"]["decision"] == "ALLOW"
    assert ledger.verify_chain()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_payload_values_are_rejected(value):
    ledger = EvidenceLedger()
    with pytest.raises(ValueError):
        ledger.append("event-1", "DECISION", "trace-1", {"value": value})
