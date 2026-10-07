from __future__ import annotations

import hashlib
import hmac
import json

from state_oracle import snapshot_hash, verify_commit_signature


def test_snapshot_hash_is_canonical():
    a = {"b": 2, "a": {"z": 1, "y": 0}}
    b = {"a": {"y": 0, "z": 1}, "b": 2}
    assert snapshot_hash(a) == snapshot_hash(b)


def test_state_oracle_signature_binds_version_and_snapshot(monkeypatch):
    secret = "test-oracle-secret"
    monkeypatch.setenv("ACTION_GATE_STATE_ORACLE_SECRET", secret)
    import state_oracle
    state_oracle.STATE_ORACLE_SECRET = secret
    payload = {"world_version": "wv-1", "snapshot": {"tool": "ready"}}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    signature = hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    assert verify_commit_signature(payload, signature)
    tampered = {"world_version": "wv-2", "snapshot": {"tool": "ready"}}
    assert not verify_commit_signature(tampered, signature)
