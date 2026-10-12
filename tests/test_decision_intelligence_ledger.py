import json

import pytest

from action_gate.decision_intelligence_ledger import DecisionLedger, LedgerError


def add(ledger, primary="ALLOW", reviewer="ALLOW", risk="LOW", component="release"):
    return ledger.append(
        component=component,
        risk=risk,
        primary_decision=primary,
        reviewer_decision=reviewer,
        evidence={"checks": ["unit-tests"], "evidence_id": "e-001"},
        source_sha="abc123",
        component_version="1.0.0",
        run_id="run-001",
    )


def test_append_and_verify_hash_chain(tmp_path):
    ledger = DecisionLedger(tmp_path / "decisions.jsonl")
    first = add(ledger)
    second = add(ledger, primary="DENY", reviewer="DENY")
    verified = ledger.verify()

    assert first["previous_hash"] == "GENESIS"
    assert second["previous_hash"] == first["record_hash"]
    assert verified["valid"] is True
    assert verified["records"] == 2


def test_disagreement_is_preserved_and_requires_review(tmp_path):
    ledger = DecisionLedger(tmp_path / "decisions.jsonl")
    record = add(ledger, primary="ALLOW", reviewer="DENY", risk="HIGH")

    assert record["agreement"] is False
    assert record["disposition"] == "REVIEW_REQUIRED"
    assert ledger.report(component="release")["disagreements"] == 1


def test_high_risk_allow_requires_review_even_when_reviewer_agrees(tmp_path):
    ledger = DecisionLedger(tmp_path / "decisions.jsonl")
    record = add(ledger, primary="ALLOW", reviewer="ALLOW", risk="CRITICAL")

    assert record["agreement"] is True
    assert record["disposition"] == "REVIEW_REQUIRED"


def test_report_groups_decisions_into_batches(tmp_path):
    ledger = DecisionLedger(tmp_path / "decisions.jsonl")
    for index in range(3):
        add(ledger, primary="ALLOW", reviewer="DENY" if index == 1 else "ALLOW")

    report = ledger.report(batch_size=2)
    assert report["total_decisions"] == 3
    assert [batch["decisions"] for batch in report["batches"]] == [2, 1]
    assert report["batches"][0]["disagreements"] == 1


def test_tampering_is_detected_before_next_append(tmp_path):
    path = tmp_path / "decisions.jsonl"
    ledger = DecisionLedger(path)
    add(ledger)
    original = json.loads(path.read_text(encoding="utf-8"))
    original["primary_decision"] = "DENY"
    path.write_text(json.dumps(original) + "\n", encoding="utf-8")

    with pytest.raises(LedgerError, match="record hash mismatch"):
        ledger.verify()
    with pytest.raises(LedgerError, match="record hash mismatch"):
        add(ledger)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"risk": "EXTREME"},
        {"primary": "MAYBE"},
        {"reviewer": "MAYBE"},
    ],
)
def test_invalid_decisions_are_rejected(tmp_path, kwargs):
    ledger = DecisionLedger(tmp_path / "decisions.jsonl")
    with pytest.raises(LedgerError):
        add(ledger, **kwargs)
