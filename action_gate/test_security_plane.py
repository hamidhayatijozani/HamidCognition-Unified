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
    assert plane.verify_integrity()["valid"] is True


def test_evidence_plane_detects_payload_tampering(monkeypatch, tmp_path):
    plane = load_plane(monkeypatch, tmp_path)
    plane.observe(
        event_type="EXECUTION", tenant_id="t1", agent_id="a1", actor_id="u1",
        session_id="s1", action="read", target="tool://safe", payload={"value": "original"},
    )
    assert plane.verify_integrity()["valid"] is True
    con = plane._connect()
    try:
        con.execute("UPDATE security_events SET payload_json = REPLACE(payload_json, 'original', 'tampered') WHERE id = 1")
        con.commit()
    finally:
        con.close()
    result = plane.verify_integrity()
    assert result["valid"] is False
    assert result["reason"] == "event_content_tampered"



def _allow_record(target="tool://safe"):
    from datetime import datetime, timedelta, timezone
    return {
        "tenant_id": "t1",
        "actor_id": "u1",
        "session_id": "s1",
        "nonce": "nonce-1",
        "action_hash": "hash-1",
        "decision": "ALLOW",
        "consumed_at": None,
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        "request": {"agent_id": "a1", "action": "read", "target": target, "session_id": "s1"},
        "approval": None,
        "evidence_state": {"status": "PASS", "contradictions": []},
        "policy_snapshot": {"policy_version": "test", "rules": []},
        "policy_version": "test",
    }


def test_kill_switch_blocks_real_execution_route(monkeypatch, tmp_path):
    plane = load_plane(monkeypatch, tmp_path)
    import app as gate
    from fastapi.testclient import TestClient
    monkeypatch.setattr(gate, "load", lambda decision_id, tenant_id: _allow_record())
    monkeypatch.setattr(gate, "require_auth", lambda authorization: None)
    monkeypatch.setattr(gate, "enforce_rate_limit", lambda authorization, tenant_id: None)
    plane.set_kill_switch(True, "e2e-incident")
    client = TestClient(gate.app)
    response = client.post(
        "/v1/action/d1/execution/reserve",
        json={"action_hash": "hash-1", "tenant_id": "t1", "actor_id": "u1", "session_id": "s1", "nonce": "nonce-1"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "security_kill_switch_active"


def test_tripwire_blocks_real_execution_route(monkeypatch, tmp_path):
    plane = load_plane(monkeypatch, tmp_path)
    import app as gate
    from fastapi.testclient import TestClient
    monkeypatch.setattr(gate, "load", lambda decision_id, tenant_id: _allow_record("decoy://secret"))
    monkeypatch.setattr(gate, "require_auth", lambda authorization: None)
    monkeypatch.setattr(gate, "enforce_rate_limit", lambda authorization, tenant_id: None)
    client = TestClient(gate.app)
    response = client.post(
        "/v1/action/d1/execution/reserve",
        json={"action_hash": "hash-1", "tenant_id": "t1", "actor_id": "u1", "session_id": "s1", "nonce": "nonce-1"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "security_tripwire_triggered"
