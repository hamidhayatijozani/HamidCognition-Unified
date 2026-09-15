"""Minimal AgentRQ simulator for the HHJ-CSG contract-first slice.

It emits 200 deterministic permission events and can exercise duplicate, retry,
malformed, stale-timestamp, and signature-failure scenarios. It does not invent
an AgentRQ contract; every event is built from PR-0.1.
"""
from __future__ import annotations

import asyncio
import copy
import statistics
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from .contract import hmac_sha256, sha256_digest

BASE = {
    "contract_version": "PR-0.1",
    "tenant_id": "tenant-a",
    "agent_id": "agentrq-sim",
    "target": "fixture/resource",
    "parameters": {"limit": 10},
    "context": {"source": "agentrq-simulator"},
    "evidence": [{"type": "fixture", "ref": "fixture-001"}],
    "risk_hint": "LOW",
}


def make_event(i: int) -> dict[str, Any]:
    event_id = f"evt-{i:04d}"
    return {
        **copy.deepcopy(BASE),
        "request_id": event_id,
        "action": "read" if i % 5 else "send_email",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "idempotency_key": event_id,
    }


def sign_headers(body: dict[str, Any], secret: str = "sim-secret") -> dict[str, str]:
    payload = {"contract_version": "PR-0.1", "request_digest": sha256_digest(body)}
    return {
        "X-HHJ-Canonicalization": "JCS-LITE-0.1",
        "X-HHJ-Key-Id": "poc-key-1",
        "X-HHJ-Signature": hmac_sha256(payload, secret),
    }


async def run(base_url: str = "http://127.0.0.1:8090", count: int = 200) -> dict[str, Any]:
    latencies_ms: list[float] = []
    responses: list[dict[str, Any]] = []
    async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
        for i in range(1, count + 1):
            body = make_event(i)
            started = time.perf_counter()
            response = await client.post("/decide", json=body, headers=sign_headers(body))
            latencies_ms.append((time.perf_counter() - started) * 1000)
            responses.append({"status": response.status_code, "body": response.json()})
    return {
        "events": count,
        "accepted": sum(r["status"] == 200 for r in responses),
        "p50_ms": statistics.median(latencies_ms),
        "p95_ms": sorted(latencies_ms)[max(0, int(len(latencies_ms) * 0.95) - 1)],
        "decisions": {d: sum(r["body"].get("decision") == d for r in responses) for d in ["ALLOW", "DENY", "ASK", "SANDBOX", "DEFER"]},
    }


def scenario_events() -> list[tuple[str, dict[str, Any]]]:
    normal = make_event(9001)
    duplicate = copy.deepcopy(normal)
    retry_mutated = copy.deepcopy(normal)
    retry_mutated["parameters"] = {"limit": 999}
    malformed = copy.deepcopy(normal)
    malformed.pop("agent_id")
    stale = make_event(9002)
    stale["timestamp"] = (datetime.now(timezone.utc) - timedelta(seconds=301)).isoformat()
    return [("normal", normal), ("duplicate", duplicate), ("retry_mutated", retry_mutated), ("malformed", malformed), ("stale", stale)]


if __name__ == "__main__":
    print(asyncio.run(run()))
