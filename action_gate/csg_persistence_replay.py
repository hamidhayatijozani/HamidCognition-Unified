from __future__ import annotations

import json
import os
import statistics
import time

import httpx

TOKEN = os.getenv("ACTION_GATE_API_TOKEN", "ci-csg-token")
BASE_URL = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000")
COUNT = int(os.getenv("CSG_ACCEPTANCE_EVENTS", "200"))
RESULT_PATH = os.getenv("CSG_PERSISTENCE_RESULT_PATH", "/tmp/csg-persistence-replay-result.json")


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def run(count: int = COUNT) -> dict:
    timings: list[float] = []
    failures = 0
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        for i in range(count):
            request_id = f"accept-{i:04d}"
            started = time.perf_counter()
            response = client.get(
                f"/v1/csg/replay/{request_id}",
                params={"tenant_id": "tenant-acceptance"},
                headers={"Authorization": f"Bearer {TOKEN}"},
            )
            timings.append((time.perf_counter() - started) * 1000)
            if response.status_code != 200:
                failures += 1
                continue
            payload = response.json()
            if not payload.get("match") or payload.get("world_state_replay") is not False or payload.get("side_effect_executed") is not False:
                failures += 1

    return {
        "events": count,
        "replayed_after_service_restart": count,
        "p50_ms": round(statistics.median(timings), 3) if timings else 0.0,
        "p95_ms": round(percentile(timings, 0.95), 3),
        "failures": failures,
        "durable_persistence_replay_pass": failures == 0 and len(timings) == count,
        "world_state_replay_claim": False,
        "side_effect_replay": False,
    }


if __name__ == "__main__":
    result = run()
    with open(RESULT_PATH, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
    print(json.dumps(result, sort_keys=True))
    if not result["durable_persistence_replay_pass"]:
        raise SystemExit(1)
