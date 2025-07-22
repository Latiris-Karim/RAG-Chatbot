from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.db.user_db import store_refresh_token, get_stored_refresh_token, delete_refresh_token
import jwt
import os
from datetime import datetime, timedelta
import secrets
import hashlib

security = HTTPBearer()
invalidated_tokens = set()

def decode_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, os.environ.get("jwt_secret"), algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def create_access_token(u_id: int) -> str:
    expires_delta = timedelta(minutes=15)
    
    payload = {
        "user_id": u_id,
        "type": "access",
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, os.environ.get("jwt_secret"), algorithm="HS256")

def create_refresh_token(u_id: int) -> str:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    store_refresh_token(u_id, token_hash)
    return token

def create_token_pair(u_id: int):
    access_token = create_access_token(u_id)
    refresh_token = create_refresh_token(u_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def validate_refresh_token(token: str, user_id: int) -> bool:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    stored_hash = get_stored_refresh_token(user_id)
    return stored_hash == token_hash if stored_hash else False

def is_token_blacklisted(token: str) -> bool:
    return token in invalidated_tokens

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if is_token_blacklisted(token):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated"
        )
    payload = decode_token(token, "access")
    return payload["user_id"]

def invalidate_token(token: str):
    try:
        payload = decode_token(token, "access")
        user_id = payload["user_id"]
        
        invalidated_tokens.add(token)
        delete_refresh_token(user_id)
        
        return True
    except HTTPException:
        invalidated_tokens.add(token)
        return False


