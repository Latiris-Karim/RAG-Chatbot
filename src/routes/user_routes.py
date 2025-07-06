from fastapi import APIRouter, Depends, Request
import src.db.user_db as user_db
from src.utils.jwt_handler import invalidate_token
from src.services.email_service import verify_emailcode
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter(prefix="/user", tags=["user"])
security = HTTPBearer()

class UserLogin(BaseModel):
    email: str
    pw: str

class VerifyEmail(BaseModel):
    code: str
    email: str

@router.post("/register")
async def register(req: UserLogin):#localstorage the email  for code verification
    email = req.email
    pw = req.pw
    result = user_db.register(email,pw)
    return result

@router.post("/login")
async def login(req: UserLogin):
    email = req.email
    pw = req.pw
    result = user_db.login(email, pw)
    return result

@router.post("/verify_code")
async def code_verifier(req:VerifyEmail):
    code = req.code
    email = req.email
    result = verify_emailcode(code, email)
    return result
 
@router.post("/logout")
async def logout( 
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    await invalidate_token(token)
    return {"message": "Successfully logged out"}



