"""Replay acceptance harness for the HHJ-CSG vertical slice."""
from __future__ import annotations

import asyncio
from typing import Any

import httpx

from .agent_rq_simulator import make_event, sign_headers


async def replay_check(app: Any, count: int = 100) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://replay") as client:
        for i in range(1, count + 1):
            body = make_event(i)
            headers = sign_headers(body)
            first = await client.post("/decide", json=body, headers=headers)
            replay = await client.post("/decide", json=body, headers=headers)
            a, b = first.json(), replay.json()
            if first.status_code != 200 or replay.status_code != 200 or a["request_digest"] != b["request_digest"] or a["decision_digest"] != b["decision_digest"] or a["metrics_snapshot"]["deterministic_score"] != b["metrics_snapshot"]["deterministic_score"]:
                mismatches.append({"event": i, "first_status": first.status_code, "replay_status": replay.status_code})
    return {"events": count, "digest_match_rate": 1.0 - len(mismatches) / count, "score_match_rate": 1.0 - len(mismatches) / count, "mismatches": mismatches}


if __name__ == "__main__":
    import action_gate.contract_app as contract_app
    print(asyncio.run(replay_check(contract_app.app)))
