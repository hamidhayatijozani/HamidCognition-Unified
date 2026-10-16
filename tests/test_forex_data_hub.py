import json
import sqlite3

import pytest

from scripts import forex_data_hub as hub


def test_bar_rejects_inconsistent_ohlc():
    with pytest.raises(ValueError, match="inconsistent OHLC"):
        hub._bar("fixture", "EURUSD", "2026-10-16T00:00:00Z", 1.1, 1.0, 0.9, 1.2)


def test_fetch_latest_falls_back_after_provider_failure(monkeypatch):
    calls = []
    def fail(pair):
        calls.append("primary")
        raise RuntimeError("offline")
    def ok(pair):
        calls.append("fallback")
        return {"source": "fixture", "symbol": pair, "timestamp": "2026-10-16T00:00:00Z"}
    monkeypatch.setattr(hub, "PROVIDERS", [("primary", fail), ("fallback", ok)])
    result = hub.fetch_latest("EUR/USD")
    assert result["source"] == "fixture"
    assert result["fallback_failures"][0]["provider"] == "primary"
    assert calls == ["primary", "fallback"]


def test_fetch_latest_fails_closed_when_all_providers_fail(monkeypatch):
    def fail(pair):
        raise RuntimeError("offline")
    monkeypatch.setattr(hub, "PROVIDERS", [("one", fail), ("two", fail)])
    with pytest.raises(RuntimeError, match="All FX providers failed"):
        hub.fetch_latest("EURUSD")


def test_persist_tick_uses_sqlite_and_jsonl(monkeypatch, tmp_path):
    monkeypatch.setattr(hub, "DB_PATH", tmp_path / "fx.db")
    monkeypatch.setattr(hub, "JSONL_PATH", tmp_path / "nested" / "ticks.jsonl")
    tick = {"source": "fixture", "symbol": "EURUSD", "timestamp": "2026-10-16T00:00:00Z",
            "received_at": "2026-10-16T00:00:01Z", "mid": 1.1}
    hub.persist_tick(tick)
    with sqlite3.connect(tmp_path / "fx.db") as conn:
        row = conn.execute("SELECT source, symbol FROM fx_ticks").fetchone()
    assert row == ("fixture", "EURUSD")
    assert json.loads((tmp_path / "nested" / "ticks.jsonl").read_text().strip()) == tick


def test_fx_hub_never_labels_provider_data_as_validated_live_execution(monkeypatch):
    monkeypatch.setattr(hub, "PROVIDERS", [("fixture", lambda pair: {
        "source": "fixture", "symbol": pair, "timestamp": "2026-10-16T00:00:00Z",
        "evidence_scope": "PROVIDER_RESPONSE_NOT_INDEPENDENTLY_VERIFIED"
    })])
    result = hub.fetch_latest("EURUSD")
    assert result["evidence_scope"] == "PROVIDER_RESPONSE_NOT_INDEPENDENTLY_VERIFIED"
