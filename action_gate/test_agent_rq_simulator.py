import importlib

import pytest
from httpx import ASGITransport, AsyncClient

from action_gate.agent_rq_simulator import make_event, sign_headers
from action_gate.replay_harness import replay_check


@pytest.fixture
def module(monkeypatch):
    monkeypatch.setenv("HHJ_CSG_HMAC_SECRET", "sim-secret")
    monkeypatch.delenv("HHJ_CSG_API_KEY", raising=False)
    import action_gate.contract_app as contract_app
    contract_app = importlib.reload(contract_app)
    contract_app._idempotency.clear()
    contract_app._audit.clear()
    return contract_app


@pytest.mark.anyio
async def test_two_hundred_event_vertical_slice(module):
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://sim") as client:
        accepted = 0
        for i in range(1, 201):
            body = make_event(i)
            response = await client.post("/decide", json=body, headers=sign_headers(body))
            assert response.status_code == 200
            accepted += 1
    assert accepted == 200


@pytest.mark.anyio
async def test_replay_is_exact_for_digest_and_score(module):
    result = await replay_check(module.app, count=100)
    assert result["digest_match_rate"] == 1.0
    assert result["score_match_rate"] == 1.0
    assert result["mismatches"] == []


@pytest.mark.anyio
async def test_retry_duplicate_is_idempotent(module):
    body = make_event(7777)
    async with AsyncClient(transport=ASGITransport(app=module.app), base_url="http://sim") as client:
        first = await client.post("/decide", json=body, headers=sign_headers(body))
        retry = await client.post("/decide", json=body, headers=sign_headers(body))
    assert first.status_code == 200
    assert retry.status_code == 200
    assert retry.json()["replayed"] is True
