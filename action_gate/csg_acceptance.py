from __future__ import annotations

import hashlib
import hmac
import json
import os
import statistics
import time
from datetime import datetime, timezone

import httpx

from canonicalization import canonicalize

TOKEN = os.getenv("ACTION_GATE_API_TOKEN", "ci-csg-token")
SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET", "ci-csg-secret")
BASE_URL = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000")


def sign(payload: dict) -> str:
    return hmac.new(SECRET.encode(), canonicalize(payload), hashlib.sha256).hexdigest()


def event(index: int) -> dict:
    action = ["read_public", "send_email", "delete_file", "transfer_funds"][index % 4]
    return {
        "contract_version": "hhj-csg/1.0", "request_id": f"accept-{index:04d}", "tenant_id": "tenant-acceptance",
        "agent_id": "agentrq-acceptance", "actor_id": "acceptance", "action": action,
        "target": "production-db" if action == "delete_file" and index % 8 == 0 else "public-resource",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "parameters": {"index": index}, "context": {"suite": "csg-acceptance"},
    }


def expected(action: str, target: str | None) -> str:
    if action in {"transfer_funds", "transfer_money"}: return "SANDBOX"
    if action in {"delete_file", "delete_customer", "delete_database"} and target and "prod" in target.lower(): return "DENY"
    if action in {"delete_file", "delete_customer", "delete_database", "send_email", "send_external_email", "http_post_external"}: return "ASK"
    return "ALLOW"


def percentile(values: list[float], p: float) -> float:
    if not values: return 0.0
    ordered = sorted(values); rank = (len(ordered) - 1) * p; low = int(rank); high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def run(count: int = 200) -> dict:
    timings: list[float] = []; replay_timings: list[float] = []; false_allow = 0; digest_mismatches = 0; score_mismatches = 0
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        records = []
        for i in range(count):
            body = event(i); headers = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": body["request_id"], "X-HCJ-Request-Signature": sign(body)}
            started = time.perf_counter(); response = client.post("/v1/csg/decide", json=body, headers=headers); timings.append((time.perf_counter() - started) * 1000)
            assert response.status_code == 200, response.text
            result = response.json(); expected_decision = expected(body["action"], body["target"])
            if result["decision"] == "ALLOW" and expected_decision != "ALLOW": false_allow += 1
            digest_mismatches += result["request_digest"] != hashlib.sha256(canonicalize(body)).hexdigest()
            score_mismatches += result["decision"] != expected_decision
            records.append((body, headers, result))
        for body, headers, original in records:
            started = time.perf_counter(); replay = client.post("/v1/csg/decide", json=body, headers=headers); replay_timings.append((time.perf_counter() - started) * 1000)
            assert replay.status_code == 200, replay.text
            result = replay.json(); digest_mismatches += result["request_digest"] != original["request_digest"]; score_mismatches += result["decision"] != original["decision"]
    return {"events": count, "replays": count, "p50_ms": round(statistics.median(timings), 3), "p95_ms": round(percentile(timings, 0.95), 3), "replay_p50_ms": round(statistics.median(replay_timings), 3), "replay_p95_ms": round(percentile(replay_timings, 0.95), 3), "digest_mismatches": digest_mismatches, "decision_mismatches": score_mismatches, "false_allow": false_allow, "replay_exact_match": digest_mismatches == 0 and score_mismatches == 0}


if __name__ == "__main__":
    print(json.dumps(run(int(os.getenv("CSG_ACCEPTANCE_EVENTS", "200"))), sort_keys=True))
