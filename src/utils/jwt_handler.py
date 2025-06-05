from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from datetime import datetime, timedelta

security = HTTPBearer()
invalidated_tokens = set()

def decode_token(token: str):
    try:
        payload = jwt.decode(token, os.environ.get("jwt_secret"), algorithms=["HS256"])
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

def create_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, os.environ.get("jwt_secret"), algorithm="HS256")

def is_token_blacklisted(token: str) -> bool:
    return token in invalidated_tokens

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if is_token_blacklisted(token):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated"
        )
    payload = decode_token(token)
    return payload["user_id"]

def invalidate_token(token: str):
    invalidated_tokens.add(token)
    return True


