from fastapi.testclient import TestClient
from app import app

def test_console_is_reachable():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "HAMIDCOGNITION" in response.text
    assert "Action Gate" in response.text
