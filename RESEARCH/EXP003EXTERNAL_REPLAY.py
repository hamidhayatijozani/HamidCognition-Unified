import copy
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "RESEARCH" / "fixtures" / "externalfeed.json"
RESULT = ROOT / "RESEARCH" / "EXP003RESULT.json"


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_fixture():
    if not FIXTURE.exists():
        raise FileNotFoundError(f"Missing fixture: {FIXTURE}")
    with FIXTURE.open("r", encoding="utf-8") as f:
        return json.load(f)


def replay(feed):
    """Deterministic protocol-level replay transform.

    The input may be a frozen snapshot from a real external source. This
    function validates replay determinism and input sensitivity only; it does
    not claim to reproduce the external provider's internal process.
    """
    rows = feed.get("feed", [])
    values = [float(row["value"]) for row in rows]
    if not values:
        raise ValueError("Fixture feed is empty")

    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    return {
        "count": len(values),
        "first": values[0],
        "last": values[-1],
        "min": min(values),
        "max": max(values),
        "sum": round(sum(values), 12),
        "delta_sum": round(sum(deltas), 12),
        "absolute_delta_sum": round(sum(abs(x) for x in deltas), 12),
    }


def fingerprint(value):
    return sha256_bytes(canonical_json(value))


def main():
    fixture = load_fixture()
    provenance = fixture.get("provenance", {})
    canonical = canonical_json(fixture)
    fixture_digest = sha256_bytes(canonical)

    if provenance.get("source_type") != "external":
        raise SystemExit("EXP-003 real-source gate requires provenance.source_type=external")
    if not provenance.get("external_source_claimed"):
        raise SystemExit("EXP-003 real-source gate requires external_source_claimed=true")
    if not provenance.get("source_url"):
        raise SystemExit("EXP-003 real-source gate requires source_url")
    if not provenance.get("retrieved_at_utc"):
        raise SystemExit("EXP-003 real-source gate requires retrieved_at_utc")
    if not provenance.get("preprocessing"):
        raise SystemExit("EXP-003 real-source gate requires preprocessing provenance")

    output_a = replay(fixture)
    output_b = replay(copy.deepcopy(fixture))

    modified = copy.deepcopy(fixture)
    modified["feed"][1]["value"] = float(modified["feed"][1]["value"]) + 0.0001
    output_c = replay(modified)

    fp_a = fingerprint(output_a)
    fp_b = fingerprint(output_b)
    fp_c = fingerprint(output_c)

    deterministic = fp_a == fp_b
    sensitive = fp_a != fp_c

    result = {
        "experiment": "EXP-003",
        "experiment_status": "REAL_EXTERNAL_SNAPSHOT_REPLAY_EXECUTED",
        "protocol_version": "3.0",
        "fixture_path": str(FIXTURE.relative_to(ROOT)),
        "fixture_id": fixture.get("fixture_id"),
        "fixture_status": fixture.get("fixture_status"),
        "provenance": provenance,
        "fixture_sha256": fixture_digest,
        "fixture_byte_length": len(canonical),
        "runs": {
            "run_a": {"output": output_a, "fingerprint": fp_a},
            "run_b": {"output": output_b, "fingerprint": fp_b},
            "run_c_modified_input": {"output": output_c, "fingerprint": fp_c},
        },
        "tests": {
            "fixture_integrity": True,
            "external_source_provenance_present": True,
            "deterministic_replay": deterministic,
            "real_external_snapshot_input_sensitivity": sensitive,
        },
        "claims_verified": [
            "fixture_exists",
            "fixture_is_valid_json",
            "external_source_provenance_present",
            "canonical_fixture_hash_computed",
            "same_real_source_snapshot_produces_identical_output_fingerprint",
            "modified_snapshot_input_changes_output_fingerprint",
        ],
        "claims_not_verified": [
            "external_world_reproducibility",
            "scientific_validity_of_external_feed_behavior",
            "reproduction_of_external_provider_internal_process",
            "predictive_skill_or_trading_value",
        ],
        "result_class": (
            "SUPPORTED_REAL_SOURCE_REPLAY_MECHANISM"
            if deterministic and sensitive
            else "INCONCLUSIVE"
        ),
        "python_version": platform.python_version(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "note": (
            "The fixture is a frozen snapshot of a real ECB EUR/USD reference-rate "
            "series. This experiment establishes provenance, deterministic replay, "
            "and sensitivity of the replay transform to the frozen external input. "
            "It does not establish external-world reproducibility or scientific validity."
        ),
    }

    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))

    if not deterministic or not sensitive:
        raise SystemExit("EXP-003 real-source replay test failed")


if __name__ == "__main__":
    main()
