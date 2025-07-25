from ragapi.main import app
from fastapi.testclient import TestClient
from src.utils.jwt_handler import create_token_pair


client = TestClient(app)

def fake_auth_header(token="test_token"):
    return {"Authorization": f"Bearer {token}"}

def real_auth_header(u_id=2):
    tokens = create_token_pair(u_id)
    access_token = tokens["access_token"]  
    return {"Authorization": f"Bearer {access_token}"}
