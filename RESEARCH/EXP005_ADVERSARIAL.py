"""EXP-005: adversarial tests of the EXP-004 evidence validator."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from EXP004_VALIDATOR import validate_exp004

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "EXP004RESULT.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def expect_valid(name: str, payload: dict) -> None:
    valid, errors = validate_exp004(payload)
    if not valid:
        raise AssertionError(f"{name}: expected VALID, got {errors}")


def expect_invalid(name: str, payload: dict) -> None:
    valid, errors = validate_exp004(payload)
    if valid:
        raise AssertionError(f"{name}: expected REJECTED artifact")


def main() -> int:
    canonical = load_artifact()
    expect_valid("canonical_artifact", canonical)

    cases = {}
    m = copy.deepcopy(canonical)
    m["interpretation"] = "SURVIVES_PRELIMINARY"
    m["promotion"] = "BLOCKED_PENDING_INDEPENDENT_REPRODUCTION"
    m["primary_summary"]["all_snapshots_positive"] = True
    cases["forged_survival_label"] = m

    m = copy.deepcopy(canonical)
    m["primary_summary"]["all_snapshots_positive"] = True
    cases["forged_positive_aggregate"] = m

    m = copy.deepcopy(canonical)
    s = m["snapshots"]["snapshot_A"]["metrics"]["5"]
    s["model_accuracy"] = s["majority_baseline_accuracy"] + 0.01
    s["accuracy_delta_vs_majority"] = 0.01
    m["primary_summary"]["snapshot_deltas_vs_majority"][0] = 0.01
    cases["one_positive_snapshot_falsification"] = m

    m = copy.deepcopy(canonical)
    m["snapshots"]["snapshot_A"]["metrics"]["5"]["accuracy_delta_vs_majority"] = 0.01
    cases["forged_delta"] = m

    m = copy.deepcopy(canonical)
    m["integrity"]["snapshots_disjoint"] = False
    cases["integrity_disjointness_forgery"] = m

    m = copy.deepcopy(canonical)
    m["snapshots"]["snapshot_B"]["metrics"]["5"]["integrity"]["future_features_used"] = True
    cases["future_feature_contamination"] = m

    m = copy.deepcopy(canonical)
    m["snapshots"]["snapshot_A"]["raw_sha256"] = "tampered"
    cases["tampered_source_fingerprint"] = m

    for name, payload in cases.items():
        expect_invalid(name, payload)

    survival = copy.deepcopy(canonical)
    for name in ("snapshot_A", "snapshot_B"):
        primary = survival["snapshots"][name]["metrics"]["5"]
        primary["model_accuracy"] = 0.60
        primary["majority_baseline_accuracy"] = 0.50
        primary["accuracy_delta_vs_majority"] = 0.10
        primary["cost_aware_return"] = 0.10
    survival["primary_summary"]["snapshot_deltas_vs_majority"] = [0.10, 0.10]
    survival["primary_summary"]["all_snapshots_positive"] = True
    survival["interpretation"] = "SURVIVES_PRELIMINARY"
    survival["promotion"] = "BLOCKED_PENDING_INDEPENDENT_REPRODUCTION"
    expect_valid("coherent_survival_path", survival)

    report = {
        "experiment": "EXP-005",
        "status": "EXECUTED_ADVERSARIAL_VALIDATOR_TEST",
        "canonical_artifact": "EXP004RESULT.json",
        "cases_total": len(cases) + 2,
        "malicious_or_inconsistent_cases_rejected": len(cases),
        "canonical_falsification_accepted": True,
        "coherent_survival_path_accepted": True,
        "validator_is_label_independent": True,
        "validator_derives_delta_from_accuracy": True,
        "result": "PASS",
        "interpretation": "Evidence validator rejected all registered adversarial mutations and accepted both coherent falsification and coherent survival paths.",
        "scope": "This validates the registered mutation set; it does not prove completeness against all possible adversarial inputs.",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
