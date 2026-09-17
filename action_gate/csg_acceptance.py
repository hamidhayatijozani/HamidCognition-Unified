from __future__ import annotations

import hashlib
import hmac
import json
import os
import statistics
import time
from datetime import datetime, timedelta, timezone

import httpx

from canonicalization import canonicalize

TOKEN = os.getenv("ACTION_GATE_API_TOKEN", "ci-csg-token")
SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET", "ci-csg-secret")
BASE_URL = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000")
RESULT_PATH = os.getenv("CSG_ACCEPTANCE_RESULT_PATH", "csg-acceptance-result.json")


def sign(payload: dict) -> str:
    return hmac.new(SECRET.encode(), canonicalize(payload), hashlib.sha256).hexdigest()


def event(index: int, tenant: str = "tenant-acceptance") -> dict:
    action = ["read_public", "send_email", "delete_file", "transfer_funds"][index % 4]
    return {
        "contract_version": "hhj-csg/1.0", "request_id": f"accept-{index:04d}", "tenant_id": tenant,
        "agent_id": "agentrq-acceptance", "actor_id": "acceptance", "action": action,
        "target": "production-db" if action == "delete_file" and index % 8 == 0 else "public-resource",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "parameters": {"index": index}, "context": {"suite": "csg-acceptance"},
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


def adversarial_ingress(client: httpx.Client) -> dict:
    base = event(9000)
    headers = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": base["request_id"], "X-HCJ-Request-Signature": sign(base)}
    malformed = dict(base); malformed.pop("contract_version")
    malformed_response = client.post("/v1/csg/decide", json=malformed, headers=headers); assert malformed_response.status_code == 422, malformed_response.text
    invalid_json = client.post("/v1/csg/decide", content=b"{not-json", headers={**headers, "Content-Type": "application/json", "Idempotency-Key": "accept-invalid-json"}); assert invalid_json.status_code == 400, invalid_json.text
    bad_signature = client.post("/v1/csg/decide", json=base, headers={**headers, "Idempotency-Key": "accept-bad-signature", "X-HCJ-Request-Signature": "0" * 64}); assert bad_signature.status_code == 401, bad_signature.text
    stale = dict(base); stale["request_id"] = "accept-stale"; stale["timestamp"] = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    stale_headers = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": stale["request_id"], "X-HCJ-Request-Signature": sign(stale)}
    stale_response = client.post("/v1/csg/decide", json=stale, headers=stale_headers); assert stale_response.status_code == 408, stale_response.text
    first = client.post("/v1/csg/decide", json=base, headers=headers); assert first.status_code == 200, first.text
    changed = dict(base); changed["parameters"] = {"index": 9999}; changed["request_id"] = base["request_id"]
    changed_headers = {**headers, "X-HCJ-Request-Signature": sign(changed)}
    conflict = client.post("/v1/csg/decide", json=changed, headers=changed_headers); assert conflict.status_code == 409, conflict.text
    other_tenant = event(9000, tenant="tenant-other"); other_tenant["request_id"] = "accept-9000-other-tenant"
    other_headers = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": other_tenant["request_id"], "X-HCJ-Request-Signature": sign(other_tenant)}
    isolated = client.post("/v1/csg/decide", json=other_tenant, headers=other_headers); assert isolated.status_code == 200, isolated.text
    return {"malformed_schema": True, "invalid_json": True, "signature_failure": True, "stale_timestamp": True, "idempotency_conflict": True, "tenant_scoped_idempotency": True}


def run(count: int = 200) -> dict:
    timings: list[float] = []; replay_timings: list[float] = []
    false_allow = 0; digest_mismatches = 0; decision_mismatches = 0; replay_failures = 0
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        adversarial = adversarial_ingress(client)
        records = []
        for i in range(count):
            body = event(i)
            headers = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": body["request_id"], "X-HCJ-Request-Signature": sign(body)}
            started = time.perf_counter(); response = client.post("/v1/csg/decide", json=body, headers=headers); timings.append((time.perf_counter() - started) * 1000)
            assert response.status_code == 200, response.text
            result = response.json(); expected_decision = expected(body["action"], body["target"])
            if result["decision"] == "ALLOW" and expected_decision != "ALLOW": false_allow += 1
            digest_mismatches += result["request_digest"] != hashlib.sha256(canonicalize(body)).hexdigest()
            decision_mismatches += result["decision"] != expected_decision
            records.append((body, result))

        # Decision Replay reconstructs only stored Request + deterministic Policy/Algorithm + recorded Decision.
        # It never re-submits the action, redeems a nonce, or claims to replay external world state.
        for body, original in records:
            started = time.perf_counter()
            replay = client.get(f"/v1/csg/replay/{body['request_id']}", params={"tenant_id": body["tenant_id"]}, headers={"Authorization": f"Bearer {TOKEN}"})
            replay_timings.append((time.perf_counter() - started) * 1000)
            assert replay.status_code == 200, replay.text
            replay_result = replay.json()
            if not replay_result.get("match"): replay_failures += 1
            digest_mismatches += not replay_result.get("request_digest_match", False)
            decision_mismatches += not replay_result.get("decision_match", False)

    return {
        "events": count,
        "decision_replays": count,
        "p50_ms": round(statistics.median(timings), 3),
        "p95_ms": round(percentile(timings, 0.95), 3),
        "replay_p50_ms": round(statistics.median(replay_timings), 3),
        "replay_p95_ms": round(percentile(replay_timings, 0.95), 3),
        "digest_mismatches": digest_mismatches,
        "decision_mismatches": decision_mismatches,
        "false_allow": false_allow,
        "replay_failures": replay_failures,
        "decision_replay_exact_match": digest_mismatches == 0 and decision_mismatches == 0 and replay_failures == 0,
        "world_state_replay_claim": False,
        "adversarial_ingress": adversarial,
    }


if __name__ == "__main__":
    result = run(int(os.getenv("CSG_ACCEPTANCE_EVENTS", "200")))
    result["timestamp_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result["contract_version"] = "hhj-csg/1.0"
    with open(RESULT_PATH, "w", encoding="utf-8") as handle: json.dump(result, handle, indent=2, sort_keys=True)
    print(json.dumps(result, sort_keys=True))
