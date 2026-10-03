import pytest


@pytest.fixture(autouse=True)
def isolate_api_token(request):
    import app as gate

    if request.module.__name__.endswith("test_csg_vertical_slice"):
        yield
        return

    previous = gate.API_TOKEN
    gate.API_TOKEN = None
    try:
        yield
    finally:
        gate.API_TOKEN = previous
