from src.besaz_innovation_engine import (
    CandidateStatus,
    InnovationKind,
    generate_candidates,
    run_sandbox,
)


def components():
    return [
        {"component_id": "COGNITION", "maturity": "PROTOTYPE", "evidence_refs": []},
        {"component_id": "EXECUTION", "maturity": "VERIFIED", "evidence_refs": ["e1"]},
        {"component_id": "FEEDBACK", "maturity": "SPECIFIED", "evidence_refs": []},
        {"component_id": "VERIFICATION", "maturity": "VERIFIED", "evidence_refs": ["e2"]},
    ]


def test_generates_multiple_innovation_modes():
    result = generate_candidates(components())
    kinds = {c.kind for c in result}
    assert len(result) >= 5
    assert InnovationKind.COMBINE in kinds
    assert InnovationKind.EXTEND in kinds
    assert InnovationKind.REVERSE in kinds
    assert InnovationKind.REMOVE in kinds
    assert InnovationKind.REORDER in kinds
    assert InnovationKind.TRANSFER in kinds
    assert InnovationKind.EMERGENT in kinds
    assert all(c.status == CandidateStatus.PROPOSED for c in result)


def test_sandbox_records_failure_instead_of_hiding_it():
    candidate = generate_candidates(components())[0]
    result = run_sandbox(candidate, {
        "baseline": {"score": 0.8},
        "variant": {"score": 0.7},
        "repeatable": True,
        "evidence": ["fixture-1"],
    })
    assert result.outcome == "FAIL"
    assert result.metrics["delta"] == -0.1
    assert result.failures
    assert result.next_action == "revise_or_reject"


def test_sandbox_requires_controlled_fixture():
    candidate = generate_candidates(components())[0]
    result = run_sandbox(candidate, {"baseline": {"score": 1}})
    assert result.outcome == "INCONCLUSIVE"
    assert result.next_action == "repair_fixture"



def test_besaz_innovate_script_generates_report_without_contract_evidence_refs(monkeypatch, tmp_path):
    import json
    import scripts.besaz_innovate as module

    output = tmp_path / "innovation-report.json"
    monkeypatch.setattr(module, "OUT", output)
    history_path = tmp_path / "experiment-history.json"
    monkeypatch.setattr(module, "HISTORY_OUT", history_path)
    monkeypatch.setenv("GITHUB_RUN_ID", "run-100")
    module.main()

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["project"] == "BESAZ"
    assert report["mode"] == "INNOVATION_SANDBOX"
    assert report["authority"] == "NONE"
    assert report["candidate_count"] > 0
    assert all(candidate["source_components"] for candidate in report["candidates"])
    assert report["experiment_count"] == 3
    assert report["execution_scope"] == "DETERMINISTIC_SYNTHETIC_SMOKE_TESTS"
    assert {e["outcome"] for e in report["experiments"]} == {"PASS", "FAIL", "INCONCLUSIVE"}
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert len(history["runs"]) == 1
    assert history["runs"][0]["run_id"] == "run-100"

    # Re-running the same workflow run must not duplicate its history entry.
    module.main()
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert len(history["runs"]) == 1


def test_history_preserves_prior_runs(monkeypatch, tmp_path):
    import json
    import scripts.besaz_innovate as module

    output = tmp_path / "innovation-report.json"
    history_path = tmp_path / "experiment-history.json"
    history_path.write_text(json.dumps({
        "project": "BESAZ",
        "scope": "SYNTHETIC_ONLY",
        "runs": [{"run_id": "older-run", "experiments": []}],
    }), encoding="utf-8")
    monkeypatch.setattr(module, "OUT", output)
    monkeypatch.setattr(module, "HISTORY_OUT", history_path)
    monkeypatch.setenv("GITHUB_RUN_ID", "new-run")
    module.main()

    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert [entry["run_id"] for entry in history["runs"]] == ["older-run", "new-run"]

def test_sandbox_rejects_non_numeric_and_non_finite_scores():
    candidate = generate_candidates(components())[0]
    bad_text = run_sandbox(candidate, {
        "baseline": {"score": "not-a-number"},
        "variant": {"score": 0.5},
    })
    assert bad_text.outcome == "INCONCLUSIVE"
    assert bad_text.next_action == "repair_fixture"

    bad_inf = run_sandbox(candidate, {
        "baseline": {"score": float("inf")},
        "variant": {"score": 0.5},
    })
    assert bad_inf.outcome == "INCONCLUSIVE"
    assert bad_inf.next_action == "repair_fixture"


def test_historical_ohlcv_parser_filters_dates_and_validates_rows():
    from src.besaz_operational_evidence import parse_ohlcv_csv

    csv_text = (
        "Date,Open,High,Low,Close,Volume\\n"
        "2023-01-03,100,110,95,105,1000\\n"
        "2023-01-02,90,102,88,100,900\\n"
        "2024-01-02,105,112,104,110,1100\\n"
    )
    rows = parse_ohlcv_csv(csv_text, "2023-01-01", "2023-12-31")
    assert [row["date"] for row in rows] == ["2023-01-02", "2023-01-03"]
    assert rows[0]["close"] == 100.0


def test_historical_ohlcv_parser_rejects_invalid_prices():
    import pytest
    from src.besaz_operational_evidence import parse_ohlcv_csv

    csv_text = "Date,Open,High,Low,Close,Volume\\n2023-01-02,100,99,95,101,10\\n2023-01-03,101,105,100,104,10\\n"
    with pytest.raises(ValueError, match="High is inconsistent"):
        parse_ohlcv_csv(csv_text, "2023-01-01", "2023-12-31")


def test_buy_hold_metrics_are_explicitly_not_predictive_edge():
    from src.besaz_operational_evidence import calculate_buy_hold_metrics

    rows = [
        {"date": "2023-01-02", "close": 100.0},
        {"date": "2023-01-03", "close": 110.0},
        {"date": "2023-01-04", "close": 99.0},
    ]
    metrics = calculate_buy_hold_metrics(rows)
    assert metrics["total_return"] == -0.01
    assert metrics["max_drawdown"] == 0.1
    assert metrics["predictive_edge"] == "NOT_TESTED"
    assert metrics["live_execution"] == "NOT_TESTED"


def test_operational_evidence_is_persisted_to_jsonl_and_sqlite(tmp_path):
    import json
    import sqlite3
    from src.besaz_operational_evidence import persist_evidence

    record = {
        "run_id": "unit-test-run",
        "timestamp": "2026-10-16T00:00:00+00:00",
        "experiment_type": "HISTORICAL_MARKET_DATA_RESEARCH",
        "symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "result": "DATA_RECEIVED_METRICS_COMPUTED",
    }
    log_path = tmp_path / "nested" / "evidence.jsonl"
    db_path = tmp_path / "nested" / "evidence.db"
    persist_evidence(record, log_path, db_path)
    assert json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])["run_id"] == "unit-test-run"
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT run_id, result FROM experiments").fetchone()
    assert row == ("unit-test-run", "DATA_RECEIVED_METRICS_COMPUTED")


def test_real_mode_never_silently_falls_back_to_synthetic(monkeypatch, tmp_path):
    import pytest
    import scripts.besaz_innovate as module

    monkeypatch.setattr(module, "OUT", tmp_path / "report.json")
    monkeypatch.setattr(module, "HISTORY_OUT", tmp_path / "history.json")
    def fail_provider(*args, **kwargs):
        raise RuntimeError("provider unavailable")
    monkeypatch.setattr(module, "fetch_stooq_daily", fail_provider)
    with pytest.raises(RuntimeError, match="provider unavailable"):
        module.main(["--data-source", "real", "--symbol", "AAPL"])
