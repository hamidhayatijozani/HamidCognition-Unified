import uuid

import pytest


@pytest.fixture(autouse=True)
def isolate_api_token(request):
    import app as gate
    from state_oracle import commit_snapshot

    if request.module.__name__.endswith("test_csg_vertical_slice"):
        yield
        return

    previous = gate.API_TOKEN
    previous_oracle_secret = gate.STATE_ORACLE_SECRET
    gate.API_TOKEN = None
    gate.STATE_ORACLE_SECRET = "ci-csg-state-oracle-secret"
    commit_snapshot(
        {"source": "pytest-fixture", "status": "ready", "execution_boundary": "test"},
        world_version=f"pytest-{uuid.uuid4().hex}",
    )
    try:
        yield
    finally:
        gate.API_TOKEN = previous
        gate.STATE_ORACLE_SECRET = previous_oracle_secret
