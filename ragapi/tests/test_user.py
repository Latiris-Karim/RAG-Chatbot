from conftest import client, fake_auth_header

def test_register_user():
    payload = {"email": "test@example.com", "pw": "password123"}
    response = client.post("/user/register", json=payload)
    assert response.status_code == 200
    assert "invalid email address" in response.json().get("message", "").lower()

def test_login_user():
    payload = {"email": "test@example.com", "pw": "password123"}
    response = client.post("/user/login", json=payload)
    assert response.status_code == 200
    assert "message" in response.json()

def test_logout_unauthorized():
    response = client.post("/user/logout", headers=fake_auth_header())
    assert response.status_code == 200

