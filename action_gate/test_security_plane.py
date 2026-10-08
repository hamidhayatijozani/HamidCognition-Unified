import importlib


def load_plane(monkeypatch, tmp_path):
    monkeypatch.setenv("ACTION_GATE_SECURITY_DB", str(tmp_path / "security.db"))
    monkeypatch.setenv("ACTION_GATE_ANOMALY_WINDOW_SECONDS", "60")
    monkeypatch.setenv("ACTION_GATE_ANOMALY_BURST_LIMIT", "2")
    monkeypatch.setenv("ACTION_GATE_ANOMALY_THRESHOLD", "1.0")
    monkeypatch.setenv("ACTION_GATE_TRIPWIRE_TARGETS", "decoy://secret")
    import security_plane
    return importlib.reload(security_plane)


def test_kill_switch_is_persistent_and_observable(monkeypatch, tmp_path):
    plane = load_plane(monkeypatch, tmp_path)
    assert plane.security_status()["kill_switch"] is False
    plane.set_kill_switch(True, "incident-test")
    assert plane.is_kill_switch_active() is True
    status = plane.security_status()
    assert status["kill_switch"] is True
    assert status["reason"] == "incident-test"


def test_tripwire_produces_security_signal(monkeypatch, tmp_path):
    plane = load_plane(monkeypatch, tmp_path)
    event = plane.observe(
        event_type="EXECUTION",
        tenant_id="t1",
        agent_id="a1",
        actor_id="u1",
        session_id="s1",
        action="read",
        target="decoy://secret",
    )
    assert event["tripwire"] is True
    assert event["anomaly_detected"] is False


def test_bounded_burst_anomaly_is_replayable(monkeypatch, tmp_path):
    plane = load_plane(monkeypatch, tmp_path)
    first = plane.observe(
        event_type="EXECUTION",
        tenant_id="t1",
        agent_id="a1",
        actor_id="u1",
        session_id="s1",
        action="read",
        target="tool://safe",
    )
    second = plane.observe(
        event_type="EXECUTION",
        tenant_id="t1",
        agent_id="a1",
        actor_id="u1",
        session_id="s1",
        action="read",
        target="tool://safe",
    )
    assert first["anomaly_score"] == 0.5
    assert second["anomaly_score"] == 1.0
    assert second["anomaly_detected"] is True
    events = plane.recent_events(2)
    assert len(events) == 2
    assert all("event_fingerprint" in e for e in events)
