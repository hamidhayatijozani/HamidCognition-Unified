"""BESAZ Innovation Sandbox: synthetic smoke tests or historical market-data evidence.

Real mode is explicitly historical research. It does not trade, predict, or claim
production performance. The default remains synthetic for backward compatibility.
"""
import argparse
import json
import os
from pathlib import Path
from time import time

from src.besaz_innovation_engine import generate_candidates, run_sandbox
from src.awareness_components import canonical_contracts
from src.besaz_operational_evidence import (
    calculate_buy_hold_metrics,
    fetch_stooq_daily,
    persist_evidence,
    utc_now,
)

OUT = Path("data/awareness/innovation-report.json")
HISTORY_OUT = Path("data/awareness/experiment-history.json")
LOG_OUT = Path("data/awareness/operational-experiments.jsonl")
DB_OUT = Path("data/awareness/experiment_history.db")


def _components():
    return [
        {
            "component_id": c.component_id,
            "maturity": c.maturity.value,
            # Static contracts have no runtime evidence_refs. Do not pretend otherwise.
            "evidence_refs": [],
            "capabilities": list(c.capabilities),
        }
        for c in canonical_contracts()
    ]


def _read_history():
    if not HISTORY_OUT.exists():
        return {"project": "BESAZ", "scope": "MIXED_EVIDENCE", "runs": []}
    try:
        doc = json.loads(HISTORY_OUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot safely read experiment history: {HISTORY_OUT}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("runs", []), list):
        raise RuntimeError(f"Unexpected experiment history schema: {HISTORY_OUT}")
    doc.setdefault("runs", [])
    return doc


def _record_run(run_id, generated_at, scope, experiments):
    history_doc = _read_history()
    history_doc["scope"] = "MIXED_EVIDENCE"
    history_doc["runs"] = [
        item for item in history_doc["runs"]
        if not (isinstance(item, dict) and item.get("run_id") == run_id)
    ]
    history_doc["runs"].append({
        "run_id": run_id,
        "generated_at_unix": generated_at,
        "execution_scope": scope,
        "experiments": experiments,
    })
    HISTORY_OUT.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_OUT.write_text(
        json.dumps(history_doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return len(history_doc["runs"])


def run_synthetic(run_id, generated_at):
    components = _components()
    candidates = generate_candidates(components)
    probe = candidates[0]
    fixtures = [
        {"name": "synthetic_improvement", "baseline": {"score": 0.50}, "variant": {"score": 0.75},
         "repeatable": True, "evidence": ["synthetic-fixture:improvement"]},
        {"name": "synthetic_regression", "baseline": {"score": 0.80}, "variant": {"score": 0.70},
         "repeatable": True, "evidence": ["synthetic-fixture:regression"]},
        {"name": "synthetic_no_change", "baseline": {"score": 0.70}, "variant": {"score": 0.70},
         "repeatable": False, "evidence": ["synthetic-fixture:no-change"]},
    ]
    experiments = []
    for fixture in fixtures:
        result = run_sandbox(probe, fixture).to_dict()
        result["fixture_name"] = fixture["name"]
        result["evidence_scope"] = "SYNTHETIC_ONLY"
        experiments.append(result)
    history = [{"candidate_id": e["candidate_id"], "outcome": e["outcome"]} for e in experiments]
    candidates = generate_candidates(components, history)
    report = {
        "project": "BESAZ", "mode": "INNOVATION_SANDBOX", "authority": "NONE",
        "generated_at_unix": generated_at, "run_id": run_id,
        "execution_scope": "DETERMINISTIC_SYNTHETIC_SMOKE_TESTS",
        "architecture_component_count": len(components), "candidate_count": len(candidates),
        "candidates": [c.to_dict() for c in candidates],
        "experiment_count": len(experiments), "experiments": experiments,
        "truth_boundary": [
            "synthetic fixture outcomes are not proof of production performance",
            "architecture contract evidence_refs are not inferred from code presence",
            "failure and inconclusive results remain visible",
        ],
        "hard_boundary": [
            "sandbox only", "no production mutation", "no self-granted authority",
            "no invented evidence", "failure must remain visible",
            "promotion requires explicit verification and approval",
        ],
    }
    return report


def run_historical(symbol, start_date, end_date, run_id, generated_at):
    # Provider errors intentionally fail the run; no synthetic fallback is permitted.
    rows = fetch_stooq_daily(symbol, start_date, end_date)
    metrics = calculate_buy_hold_metrics(rows)
    record = {
        "run_id": run_id,
        "timestamp": utc_now(),
        "experiment_type": "HISTORICAL_MARKET_DATA_RESEARCH",
        "evidence_scope": "HISTORICAL_PROVIDER_DATA",
        "provider": "Stooq public daily CSV",
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "result": "DATA_RECEIVED_METRICS_COMPUTED",
        "metrics": metrics,
        "bars": rows,
        "authority": "NONE",
        "live_execution": "NOT_TESTED",
        "predictive_edge": "NOT_TESTED",
    }
    persist_evidence(record, LOG_OUT, DB_OUT)
    return {
        "project": "BESAZ", "mode": "INNOVATION_SANDBOX", "authority": "NONE",
        "generated_at_unix": generated_at, "run_id": run_id,
        "execution_scope": "HISTORICAL_MARKET_DATA_RESEARCH",
        "evidence_scope": "HISTORICAL_PROVIDER_DATA",
        "provider": "Stooq public daily CSV", "symbol": symbol,
        "start_date": start_date, "end_date": end_date,
        "bar_count": len(rows), "metrics": metrics,
        "evidence_log": str(LOG_OUT), "evidence_database": str(DB_OUT),
        "truth_boundary": [
            "historical market data received from external provider",
            "buy-and-hold benchmark is not a predictive strategy",
            "predictive edge and live execution have not been tested",
        ],
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-source", choices=("synthetic", "real"), default="synthetic")
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--start-date", default="2023-01-01")
    parser.add_argument("--end-date", default="2023-12-31")
    args = parser.parse_args(argv)

    generated_at = int(time())
    run_id = os.environ.get("GITHUB_RUN_ID") or f"local-{generated_at}"
    if args.data_source == "real":
        report = run_historical(args.symbol, args.start_date, args.end_date, run_id, generated_at)
        experiments = [{
            "experiment_type": report["execution_scope"],
            "outcome": "PASS" if report["bar_count"] >= 2 else "FAIL",
            "evidence_scope": report["evidence_scope"],
            "metrics": report["metrics"],
        }]
        scope = "HISTORICAL_MARKET_DATA_RESEARCH"
    else:
        report = run_synthetic(run_id, generated_at)
        experiments = report["experiments"]
        scope = report["execution_scope"]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    history_runs = _record_run(run_id, generated_at, scope, experiments)
    print(f"wrote {OUT}; scope={scope}; experiments={len(experiments)}; history_runs={history_runs}")


if __name__ == "__main__":
    main()
