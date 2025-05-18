from fastapi import APIRouter, Depends
import src.db.user_db as user_db
from src.utils.jwt_handler import get_current_user
router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register")
async def register(email: str, pw: str):
    result = user_db.register(email,pw)
    return result

@router.post("/login")
async def login(email: str, pw: str):
    result = user_db.login(email, pw)
    return result

@router.post("/test")
async def create_post(content: str,current_user_id: int = Depends(get_current_user)):
    return "testing protected route", current_user_id
