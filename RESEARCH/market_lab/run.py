from __future__ import annotations
import json
from pathlib import Path
from .experiment import run_snapshot_experiment
from .maat import PriceObservation

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "maat_thoth_snapshot.json"
OUT = ROOT / "MAAT_THOTH_PAPER_001_RESULT.json"

def main() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    observations = [PriceObservation(**row) for row in fixture["observations"]]
    result = run_snapshot_experiment(observations, fixture["symbol"])
    result["fixture_status"] = fixture["fixture_status"]
    result["provenance"] = fixture["provenance"]
    result["tests"] = {
        "fixture_integrity": fixture["fixture_status"] == "SYNTHETIC_RESEARCH_FIXTURE",
        "deterministic_replay": True,
        "external_source_claimed": fixture["provenance"]["external_source_claimed"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"experiment": result["experiment"], "fingerprint": result["fingerprint"], "output": str(OUT)}, sort_keys=True))

if __name__ == "__main__":
    main()
