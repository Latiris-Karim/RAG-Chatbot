from fastapi import APIRouter, Depends, Request
import src.db.user_db as user_db
from src.utils.jwt_handler import invalidate_token, create_token_pair
from src.db.user_db import verify_email_code
from src.services.email_service import Emails
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import hashlib

router = APIRouter(prefix="/user", tags=["user"])
security = HTTPBearer()

class UserLogin(BaseModel):
    email: str
    pw: str

class VerifyEmail(BaseModel):
    code: str
    email: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register")
async def register(req: UserLogin):
    email = req.email
    pw = req.pw
    result = user_db.register(email, pw)
    code = result.pop("code", None)
    if code:
        Emails().send_verification_email(email, code)
    return result

@router.post("/login")
async def login(req: UserLogin):
    email = req.email
    pw = req.pw
    result = user_db.login(email, pw)
    return result

@router.post("/verify_code")
async def code_verifier(req: VerifyEmail):
    return verify_email_code(req.code, req.email)

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    invalidate_token(token)
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_access_token(req: RefreshRequest):
    token_hash = hashlib.sha256(req.refresh_token.encode()).hexdigest()
    user_id = user_db.get_user_by_refresh_token(token_hash)
    return create_token_pair(user_id)
