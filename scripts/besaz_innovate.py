"""Generate candidates and execute deterministic synthetic smoke experiments."""
import json
import os
from pathlib import Path
from time import time

from src.besaz_innovation_engine import generate_candidates, run_sandbox
from src.awareness_components import canonical_contracts

OUT = Path("data/awareness/innovation-report.json")
HISTORY_OUT = Path("data/awareness/experiment-history.json")


def main() -> None:
    contracts = canonical_contracts()
    components = [
        {
            "component_id": c.component_id,
            "maturity": c.maturity.value,
            # Static contracts have no runtime evidence_refs. Do not pretend otherwise.
            "evidence_refs": [],
            "capabilities": list(c.capabilities),
        }
        for c in contracts
    ]

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

    history = [
        {"candidate_id": e["candidate_id"], "outcome": e["outcome"]}
        for e in experiments
    ]
    candidates = generate_candidates(components, history)

    report = {
        "project": "BESAZ",
        "mode": "INNOVATION_SANDBOX",
        "authority": "NONE",
        "generated_at_unix": int(time()),
        "execution_scope": "DETERMINISTIC_SYNTHETIC_SMOKE_TESTS",
        "architecture_component_count": len(components),
        "candidate_count": len(candidates),
        "candidates": [c.to_dict() for c in candidates],
        "experiment_count": len(experiments),
        "experiments": experiments,
        "truth_boundary": [
            "synthetic fixture outcomes are not proof of production performance",
            "architecture contract evidence_refs are not inferred from code presence",
            "failure and inconclusive results remain visible",
        ],
        "hard_boundary": [
            "sandbox only",
            "no production mutation",
            "no self-granted authority",
            "no invented evidence",
            "failure must remain visible",
            "promotion requires explicit verification and approval",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    run_id = os.environ.get("GITHUB_RUN_ID") or f"local-{generated_at}"
    if HISTORY_OUT.exists():
        try:
            history_doc = json.loads(HISTORY_OUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Cannot safely read experiment history: {HISTORY_OUT}") from exc
        if not isinstance(history_doc, dict) or not isinstance(history_doc.get("runs", []), list):
            raise RuntimeError(f"Unexpected experiment history schema: {HISTORY_OUT}")
    else:
        history_doc = {"project": "BESAZ", "scope": "SYNTHETIC_ONLY", "runs": []}
    history_doc.setdefault("runs", [])
    history_doc["runs"] = [item for item in history_doc["runs"] if not (isinstance(item, dict) and item.get("run_id") == run_id)]
    history_doc["runs"].append({"run_id": run_id, "generated_at_unix": generated_at, "execution_scope": "DETERMINISTIC_SYNTHETIC_SMOKE_TESTS", "experiments": experiments})
    HISTORY_OUT.write_text(json.dumps(history_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report["run_id"] = run_id
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}; candidates={len(candidates)} experiments={len(experiments)} history_runs={len(history_doc['runs'])}")


if __name__ == "__main__":
    main()
