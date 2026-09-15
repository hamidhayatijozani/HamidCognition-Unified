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

    This is intentionally not claimed to model a real external system. It
    converts an ordered feed into a stable trajectory summary so replay
    identity and input sensitivity can be tested without hidden state.
    """
    rows = feed.get("feed", [])
    values = [float(row["value"]) for row in rows]
    if not values:
        raise ValueError("Fixture feed is empty")

    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    summary = {
        "count": len(values),
        "first": values[0],
        "last": values[-1],
        "min": min(values),
        "max": max(values),
        "sum": round(sum(values), 12),
        "delta_sum": round(sum(deltas), 12),
        "absolute_delta_sum": round(sum(abs(x) for x in deltas), 12),
    }
    return summary


def fingerprint(value):
    return sha256_bytes(canonical_json(value))


def main():
    fixture = load_fixture()
    canonical = canonical_json(fixture)
    fixture_digest = sha256_bytes(canonical)

    output_a = replay(fixture)
    output_b = replay(copy.deepcopy(fixture))

    modified = copy.deepcopy(fixture)
    modified["feed"][1]["value"] = float(modified["feed"][1]["value"]) + 0.1
    output_c = replay(modified)

    fp_a = fingerprint(output_a)
    fp_b = fingerprint(output_b)
    fp_c = fingerprint(output_c)

    deterministic = fp_a == fp_b
    sensitive = fp_a != fp_c

    result = {
        "experiment": "EXP-003",
        "experiment_status": "MECHANISM_LEVEL_EXECUTED",
        "protocol_version": "2.0",
        "fixture_path": str(FIXTURE.relative_to(ROOT)),
        "fixture_id": fixture.get("fixture_id"),
        "fixture_status": fixture.get("fixture_status"),
        "fixture_sha256": fixture_digest,
        "fixture_byte_length": len(canonical),
        "runs": {
            "run_a": {"output": output_a, "fingerprint": fp_a},
            "run_b": {"output": output_b, "fingerprint": fp_b},
            "run_c_modified_input": {"output": output_c, "fingerprint": fp_c},
        },
        "tests": {
            "fixture_integrity": True,
            "deterministic_replay": deterministic,
            "external_feed_sensitivity": sensitive,
        },
        "claims_verified": [
            "fixture_exists",
            "fixture_is_valid_json",
            "canonical_fixture_hash_computed",
            "same_input_produces_identical_output_fingerprint",
            "modified_input_changes_output_fingerprint",
        ],
        "claims_not_verified": [
            "external_world_reproducibility",
            "scientific_validity_of_external_feed_behavior",
            "real_external_source_sensitivity",
        ],
        "result_class": "SUPPORTED_MECHANISM_ONLY" if deterministic and sensitive else "INCONCLUSIVE",
        "python_version": platform.python_version(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "note": "The committed fixture is synthetic. This experiment validates deterministic replay and input sensitivity of the protocol-level transform only; it is not external-world evidence.",
    }

    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))

    if not deterministic or not sensitive:
        raise SystemExit("EXP-003 mechanism test failed")


if __name__ == "__main__":
    main()
