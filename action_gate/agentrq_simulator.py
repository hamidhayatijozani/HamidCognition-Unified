from __future__ import annotations

import hashlib
import hmac
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

import httpx

from canonicalization import canonicalize

TOKEN = os.getenv("ACTION_GATE_API_TOKEN", "ci-csg-token")
SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET", "ci-csg-secret")
BASE_URL = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000")


def sign(payload: dict) -> str:
    return hmac.new(SECRET.encode(), canonicalize(payload), hashlib.sha256).hexdigest()


def make_event(index: int, mode: str = "valid") -> dict:
    action = ["read_public", "send_email", "delete_file", "transfer_funds"][index % 4]
    event = {
        "contract_version": "hhj-csg/1.0",
        "request_id": f"evt-{index:04d}",
        "tenant_id": "tenant-sim",
        "agent_id": "agentrq-simulator",
        "actor_id": "sim-actor",
        "action": action,
        "target": "production-db" if action == "delete_file" and index % 8 == 0 else "public-resource",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": {"index": index, "nonce": uuid.uuid4().hex},
        "context": {"scenario": mode, "seed": 42},
    }
    if mode == "malformed":
        event.pop("contract_version")
    return event


def run(count: int = 200, base_url: str = BASE_URL) -> dict:
    rng = random.Random(42)
    results = {"sent": 0, "accepted": 0, "rejected": 0, "duplicates": 0, "timeouts": 0, "signature_failures": 0, "malformed": 0, "responses": []}
    with httpx.Client(base_url=base_url, timeout=2.0) as client:
        for index in range(count):
            mode = rng.choice(["valid"] * 7 + ["malformed", "signature_failure", "duplicate", "timeout"])
            event = make_event(index, mode)
            headers = {"Authorization": f"Bearer {TOKEN}", "Idempotency-Key": event["request_id"]}
            if mode != "malformed":
                headers["X-HCJ-Request-Signature"] = sign(event)
            if mode == "signature_failure":
                headers["X-HCJ-Request-Signature"] = "0" * 64
            try:
                results["sent"] += 1
                response = client.post("/v1/csg/decide", json=event, headers=headers)
                if response.status_code == 200:
                    results["accepted"] += 1
                    results["responses"].append(response.json())
                else:
                    results["rejected"] += 1
                    if mode == "malformed": results["malformed"] += 1
                    if mode == "signature_failure": results["signature_failures"] += 1
                    if mode == "duplicate": results["duplicates"] += 1
            except httpx.TimeoutException:
                results["timeouts"] += 1
    return results


if __name__ == "__main__":
    result = run(int(os.getenv("CSG_SIMULATOR_EVENTS", "200")))
    print(json.dumps({k: v for k, v in result.items() if k != "responses"}, sort_keys=True))
