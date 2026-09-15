"""Independent semantic validator for EXP-004 result artifacts.

The validator derives the expected interpretation from the evidence fields instead
of trusting the artifact's interpretation/promotion labels. This is deliberately
small and deterministic so it can itself be subjected to adversarial mutation tests.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ValidationError(AssertionError):
    pass


def _require(condition: bool, message: str, errors: List[str]) -> None:
    if not condition:
        errors.append(message)


def validate_exp004(payload: Dict[str, Any]) -> tuple[bool, List[str]]:
    errors: List[str] = []

    _require(isinstance(payload, dict), "artifact_not_object", errors)
    if errors:
        return False, errors

    _require(payload.get("experiment") == "EXP-004", "wrong_experiment", errors)
    _require(payload.get("status") == "EXECUTED_REAL_EXTERNAL_WALK_FORWARD", "wrong_status", errors)

    integrity = payload.get("integrity")
    _require(isinstance(integrity, dict), "integrity_missing", errors)
    if isinstance(integrity, dict):
        _require(integrity.get("chronological") is True, "integrity_not_chronological", errors)
        _require(integrity.get("future_features_used") is False, "future_features_used", errors)
        _require(integrity.get("test_tuning") is False, "test_tuning", errors)
        _require(integrity.get("snapshots_disjoint") is True, "snapshots_not_disjoint", errors)
        _require(integrity.get("snapshot_fingerprints_present") is True, "snapshot_fingerprints_missing", errors)

    snapshots = payload.get("snapshots")
    _require(isinstance(snapshots, dict), "snapshots_missing", errors)
    _require(set(snapshots.keys()) == {"snapshot_A", "snapshot_B"}, "snapshot_set_invalid", errors)

    primary_deltas: List[float] = []
    primary_costs: List[float] = []
    snapshot_integrity_ok = True

    if isinstance(snapshots, dict):
        for name in ("snapshot_A", "snapshot_B"):
            snap = snapshots.get(name)
            _require(isinstance(snap, dict), f"{name}_not_object", errors)
            if not isinstance(snap, dict):
                snapshot_integrity_ok = False
                continue

            raw_sha = snap.get("raw_sha256")
            obs = snap.get("observations")
            metrics = snap.get("metrics")
            _require(isinstance(raw_sha, str) and len(raw_sha) == 64 and all(c in "0123456789abcdef" for c in raw_sha), f"{name}_sha_invalid", errors)
            _require(isinstance(obs, int) and obs >= 500, f"{name}_observations_invalid", errors)
            _require(isinstance(metrics, dict) and "5" in metrics, f"{name}_primary_metrics_missing", errors)
            if not (isinstance(raw_sha, str) and len(raw_sha) == 64):
                snapshot_integrity_ok = False
            if not (isinstance(obs, int) and obs >= 500):
                snapshot_integrity_ok = False

            primary = metrics.get("5") if isinstance(metrics, dict) else None
            if not isinstance(primary, dict):
                snapshot_integrity_ok = False
                continue

            delta = primary.get("accuracy_delta_vs_majority")
            cost = primary.get("cost_aware_return")
            chronological = primary.get("integrity", {}).get("chronological") is True
            future_free = primary.get("integrity", {}).get("future_features_used") is False
            untuned = primary.get("integrity", {}).get("test_tuning") is False
            _require(isinstance(delta, (int, float)), f"{name}_delta_invalid", errors)
            _require(isinstance(cost, (int, float)), f"{name}_cost_invalid", errors)
            _require(chronological, f"{name}_metric_not_chronological", errors)
            _require(future_free, f"{name}_metric_future_features", errors)
            _require(untuned, f"{name}_metric_test_tuning", errors)
            if isinstance(delta, (int, float)) and isinstance(cost, (int, float)):
                primary_deltas.append(float(delta))
                primary_costs.append(float(cost))

    _require(len(primary_deltas) == 2, "primary_delta_count_invalid", errors)
    _require(len(primary_costs) == 2, "primary_cost_count_invalid", errors)

    if len(primary_deltas) == 2 and len(primary_costs) == 2:
        derived_survival = (
            snapshot_integrity_ok
            and all(d > 0 for d in primary_deltas)
            and all(c > 0 for c in primary_costs)
        )
        expected_interpretation = "SURVIVES_PRELIMINARY" if derived_survival else "FAILS_PRIMARY_GATE"
        expected_promotion = (
            "BLOCKED_PENDING_INDEPENDENT_REPRODUCTION"
            if derived_survival
            else "CLAIM_FALSIFIED_UNDER_PREREGISTERED_GATE"
        )
        _require(payload.get("interpretation") == expected_interpretation, "interpretation_not_derived_from_evidence", errors)
        _require(payload.get("promotion") == expected_promotion, "promotion_not_derived_from_evidence", errors)

        summary = payload.get("primary_summary")
        _require(isinstance(summary, dict), "primary_summary_missing", errors)
        if isinstance(summary, dict):
            declared = summary.get("snapshot_deltas_vs_majority")
            _require(isinstance(declared, list) and len(declared) == 2, "declared_delta_vector_invalid", errors)
            if isinstance(declared, list) and len(declared) == 2:
                _require(all(isinstance(x, (int, float)) for x in declared), "declared_delta_type_invalid", errors)
                if all(isinstance(x, (int, float)) for x in declared):
                    _require(all(abs(float(a) - float(b)) < 1e-12 for a, b in zip(declared, primary_deltas)), "declared_delta_vector_mismatch", errors)
            _require(summary.get("all_snapshots_positive") is derived_survival, "all_snapshots_positive_inconsistent", errors)

    return len(errors) == 0, errors


def assert_valid(payload: Dict[str, Any]) -> None:
    valid, errors = validate_exp004(payload)
    if not valid:
        raise ValidationError("; ".join(errors))
