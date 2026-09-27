from __future__ import annotations

import hashlib
import json
from pathlib import Path

from shock_recovery import RecoveryConfig, run_trajectory

ROOT = Path(__file__).resolve().parent
CONFIG = RecoveryConfig()


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    scenarios = {
        "no_shock": [0.0] * 12,
        "shock_degradation": [0.0, 10.0],
        "persistent_shock": [10.0] * 20,
        "shock_removal_recovery": [0.0, 10.0, 8.0, 6.0, 4.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.0],
    }
    trajectories = {name: run_trajectory(values, config=CONFIG) for name, values in scenarios.items()}
    replay = run_trajectory(scenarios["shock_removal_recovery"], config=CONFIG)
    evidence = {
        "schema": "PST-SHOCK-RECOVERY-EVIDENCE-v1",
        "engine": "research_recovery_v1.1",
        "canonical_boundary": "frozen",
        "commercial_boundary": "excluded",
        "config": {"t_min": CONFIG.t_min, "t_max": CONFIG.t_max, "lambda_recovery": CONFIG.lambda_recovery, "lambda_shock": CONFIG.lambda_shock, "shock_scale": CONFIG.shock_scale},
        "trajectories": trajectories,
        "replay_sha256": digest(replay),
    }
    out = ROOT / "EVIDENCE_PACK.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"evidence_pack": str(out), "sha256": digest(evidence), "replay_sha256": evidence["replay_sha256"], "final_recovered_T": trajectories["shock_removal_recovery"][-1]["T"], "persistent_final_T": trajectories["persistent_shock"][-1]["T"]}, sort_keys=True))


if __name__ == "__main__":
    main()
