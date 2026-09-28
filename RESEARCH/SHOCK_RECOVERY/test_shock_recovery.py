import hashlib
import json

from RESEARCH.SHOCK_RECOVERY.shock_recovery import RecoveryConfig, RecoveryEngine


def run(ds):
    engine = RecoveryEngine(RecoveryConfig())
    return [engine.step(float(d)) for d in ds]


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main():
    results = {}

    no_shock = run([0.0] * 10)
    results["1_no_shock"] = {
        "pass": all(abs(x["T"] - 0.5) < 1e-12 for x in no_shock)
        and all(x["R"] == 0 for x in no_shock),
        "final_T": no_shock[-1]["T"],
    }

    shocked = run([0.0, 10.0])
    results["2_shock_degradation"] = {
        "pass": shocked[-1]["T"] < shocked[0]["T"],
        "degraded_T": shocked[-1]["T"],
    }

    persistent = run([10.0] * 20)
    results["3_persistent_shock_no_recovery"] = {
        "pass": all(x["R"] == 0 for x in persistent)
        and all(
            persistent[i]["T"] <= persistent[i - 1]["T"] + 1e-12
            for i in range(1, len(persistent))
        ),
        "min_T_reached": min(x["T"] for x in persistent),
        "all_recovery_gates_zero": all(x["R"] == 0 for x in persistent),
    }

    removal = run([10.0] * 3 + [0.0] * 10)
    shocked_T = removal[2]["T"]
    recovered = removal[3:]
    results["4_shock_removal_recovery"] = {
        "pass": recovered[0]["R"] == 1
        and all(
            recovered[i]["T"] >= recovered[i - 1]["T"] - 1e-12
            for i in range(1, len(recovered))
        ),
        "initial_shocked_T": shocked_T,
        "final_recovered_T": recovered[-1]["T"],
    }

    input_sequence = [0.0, 10.0, 10.0, 10.0, 0.0, 0.0, 0.0]
    trajectory = run(input_sequence)
    payload = canonical_json(trajectory)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    replay_digest = hashlib.sha256(
        canonical_json(run(input_sequence)).encode()
    ).hexdigest()
    results["5_replay_sha256_integrity"] = {
        "pass": digest == replay_digest,
        "sha256": digest,
    }

    if not all(value["pass"] for value in results.values()):
        raise SystemExit(json.dumps(results, indent=2, sort_keys=True))

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
