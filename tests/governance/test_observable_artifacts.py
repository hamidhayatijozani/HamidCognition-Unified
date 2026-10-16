from governance.observable_artifacts import ObservableArtifact
from governance.replay_verifier import ReplayVerifier


def artifact():
    return ObservableArtifact(
        trace_id="trace-1", agent_id="agent-1", timestamp="2026-10-16T12:00:00+00:00",
        claims=[{"id": "c1", "text": "example"}], evidence=[{"id": "e1"}],
        tool_events=[], confidence=0.7, decision_object={"action": "ASK"},
        execution_result={"status": "not_executed"},
    )


def test_artifact_validates_and_round_trips_fingerprint():
    item = artifact()
    assert item.validate()
    fingerprint = ReplayVerifier.fingerprint(item)
    assert ReplayVerifier.verify(item, fingerprint)


def test_invalid_confidence_rejected():
    item = artifact()
    item.confidence = 2.0
    assert not item.validate()


def test_changed_artifact_fails_replay():
    item = artifact()
    fingerprint = ReplayVerifier.fingerprint(item)
    item.execution_result["status"] = "executed"
    assert not ReplayVerifier.verify(item, fingerprint)
