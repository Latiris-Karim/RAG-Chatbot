from conftest import client, fake_auth_header

def test_get_display_settings_unauthorized():
    response = client.get("/settings/display", headers=fake_auth_header())
    assert response.status_code == 401

def test_change_password_unauthorized():
    payload = {"pw": "newPassword123!"}
    response = client.post("/settings/change_pw", headers=fake_auth_header(), json=payload)
    assert response.status_code == 401

def test_change_email_request_unauthorized():
    payload = {"newEmail": "new@example.com"}
    response = client.post("/settings/change_email_request", headers=fake_auth_header(), json=payload)
    assert response.status_code == 401

def test_delete_account_unauthorized():
    response = client.post("/settings/delete_account", headers=fake_auth_header())
    assert response.status_code == 401



