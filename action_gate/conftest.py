import pytest


@pytest.fixture(autouse=True)
def isolate_api_token(request):
    import app as gate

    previous = gate.API_TOKEN
    if request.module.__name__.endswith("test_csg_vertical_slice"):
        gate.API_TOKEN = "ci-csg-token"
    else:
        gate.API_TOKEN = None
    try:
        yield
    finally:
        gate.API_TOKEN = previous
