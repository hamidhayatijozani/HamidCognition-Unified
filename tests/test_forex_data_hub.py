import csv
import json

import pytest

from scripts import forex_data_hub as hub


def test_live_requires_key(monkeypatch):
    monkeypatch.setattr(hub, "_get_text", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("network must not run")))
    with pytest.raises(hub.FeedError, match="TWELVEDATA_API_KEY"):
        hub.fetch_live("")


def test_live_parses_and_marks_scope(monkeypatch):
    payload = json.dumps({
        "values": [
            {"datetime": "2026-10-23 10:05:00", "open": "1.08", "high": "1.09",
             "low": "1.07", "close": "1.085", "volume": None},
            {"datetime": "2026-10-23 10:00:00", "open": "1.07", "high": "1.08",
             "low": "1.06", "close": "1.08", "volume": None},
        ]
    })
    monkeypatch.setattr(hub, "_get_text", lambda *_args, **_kwargs: payload)
    rows = hub.fetch_live("test-key", 2)
    assert len(rows) == 2
    assert rows[0]["timestamp"] == "2026-10-23 10:00:00"
    assert {r["provider"] for r in rows} == {"twelvedata"}
    assert {r["data_scope"] for r in rows} == {"LIVE_5M"}


def test_invalid_ohlc_is_rejected():
    with pytest.raises(hub.FeedError, match="OHLC"):
        hub._validate_ohlc(
            {"open": 1.1, "high": 1.0, "low": 0.9, "close": 1.0},
            "2026-10-23", "fixture", "HISTORICAL_DAILY",
        )


def test_historical_parser_marks_daily_scope(monkeypatch):
    monkeypatch.setattr(
        hub, "_get_text",
        lambda *_args, **_kwargs: "Date,Open,High,Low,Close,Volume\n2026-10-22,1.08,1.09,1.07,1.085,0\n",
    )
    rows = hub.fetch_historical()
    assert len(rows) == 1
    assert rows[0]["provider"] == "stooq"
    assert rows[0]["data_scope"] == "HISTORICAL_DAILY"


def test_write_evidence_rejects_mixed_scope(tmp_path):
    rows = [{
        "timestamp": "2026-10-23 10:00:00", "symbol": "EUR/USD",
        "open": "1.07", "high": "1.08", "low": "1.06", "close": "1.08",
        "volume": "", "provider": "twelvedata", "data_scope": "LIVE_5M",
    }]
    with pytest.raises(hub.FeedError, match="scope"):
        hub.write_evidence(rows, tmp_path / "data.csv", tmp_path / "evidence.json", "historical")


def test_write_evidence_records_provenance_and_no_synthetic_fallback(tmp_path):
    rows = [{
        "timestamp": "2026-10-23 10:00:00", "symbol": "EUR/USD",
        "open": "1.07", "high": "1.08", "low": "1.06", "close": "1.08",
        "volume": "", "provider": "twelvedata", "data_scope": "LIVE_5M",
    }]
    metadata = hub.write_evidence(rows, tmp_path / "data.csv", tmp_path / "evidence.json", "live")
    assert metadata["synthetic_fallback"] is False
    assert metadata["data_scope"] == "LIVE_5M"
    assert metadata["observation_count"] == 1
    with (tmp_path / "data.csv").open(encoding="utf-8", newline="") as handle:
        saved = list(csv.DictReader(handle))
    assert saved[0]["provider"] == "twelvedata"
    assert json.loads((tmp_path / "evidence.json").read_text())["claim_boundary"].startswith("Data retrieval only")
