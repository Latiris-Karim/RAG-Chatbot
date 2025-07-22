from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_login():
    response = client.get("/user/login")
    assert response.status_code == 200
    assert response.json() == {}
