from conftest import client, fake_auth_header

def test_create_chatroom_unauthorized():
    response = client.post("/chat/create", headers=fake_auth_header())
    assert response.status_code == 401

def test_send_message_unauthorized():
    payload = {"txt": "Hello!", "chatroom_id": 1}
    response = client.post("/chat/send", headers=fake_auth_header())
    assert response.status_code == 401
   
def test_get_chatrooms_unauthorized():
    response = client.get("/chat/get_chatrooms", headers=fake_auth_header())
    assert response.status_code == 401

def test_get_messages_unauthorized():
    response = client.get("/chat/get_msgs?chatroom_id=1", headers=fake_auth_header())
    assert response.status_code == 401




