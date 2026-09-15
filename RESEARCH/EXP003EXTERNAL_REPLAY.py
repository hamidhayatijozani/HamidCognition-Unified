import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "RESEARCH" / "fixtures" / "externalfeed.json"
RESULT = ROOT / "RESEARCH" / "EXP003RESULT.json"


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_fixture():
    if not FIXTURE.exists():
        raise FileNotFoundError(f"Missing fixture: {FIXTURE}")
    with FIXTURE.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    fixture = load_fixture()
    canonical = canonical_json(fixture)
    digest = sha256_bytes(canonical)

    result = {
        "experiment": "EXP-003",
        "experiment_status": "FIXTURE_EXECUTION_ONLY",
        "fixture_path": str(FIXTURE.relative_to(ROOT)),
        "fixture_id": fixture.get("fixture_id"),
        "fixture_status": fixture.get("fixture_status"),
        "fixture_sha256": digest,
        "fixture_byte_length": len(canonical),
        "python_version": platform.python_version(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "claims_verified": [
            "fixture_exists",
            "fixture_is_valid_json",
            "canonical_fixture_hash_computed",
            "experiment_script_executed",
        ],
        "claims_not_verified": [
            "external_feed_reproducibility",
            "replay_determinism",
            "external_feed_sensitivity",
            "scientific_validity_of_external_feed_behavior",
        ],
        "note": "The committed fixture is explicitly synthetic. This run validates execution plumbing only and must not be interpreted as external-world evidence.",
    }

    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
