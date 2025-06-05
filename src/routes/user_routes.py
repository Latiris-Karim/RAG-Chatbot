from fastapi import APIRouter, Depends
import src.db.user_db as user_db
from src.utils.jwt_handler import get_current_user, invalidate_token
from src.services.email_service import verify_emailcode
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/user", tags=["user"])
security = HTTPBearer()

@router.post("/register")
async def register(email: str, pw: str):#client should cache / localstorage the email  for code verification
    result = user_db.register(email,pw)
    return result

@router.post("/login")
async def login(email: str, pw: str):
    result = user_db.login(email, pw)
    return result

@router.post("/verify_code")
async def code_verifier(code: str, email: str):
    result = verify_emailcode(code, email)
    return result
 
@router.post("/logout")
async def logout( 
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    await invalidate_token(token)
    return {"message": "Successfully logged out"}

