from fastapi import APIRouter, Depends
from src.utils.jwt_handler import get_current_user
from src.db.settings_db import change_pw, user_info, reset_password, forgot_pw, delete_account, change_email, change_email_request
from src.db.subscription_db import get_sub_id
from src.services.email_service import Emails
from src.services.subscription_service import cancel_stripe_subscription
from pydantic import BaseModel
import os

router = APIRouter(prefix="/settings", tags=["settings"])

class PwChange(BaseModel):
    pw: str

class PwForgot(BaseModel):
    token: str
    pw: str

class PwRequest(BaseModel):
    email: str

class NewEmailRequest(BaseModel):
    newEmail: str

class NewEmailChange(BaseModel):
    code: str

@router.get('/display')
async def display(u_id: int = Depends(get_current_user)):
    return user_info(u_id)

@router.post('/change_pw')
async def change_current_pw(req: PwChange, u_id: int = Depends(get_current_user)):
    return change_pw(u_id, req.pw)

@router.post('/request_pw_change')
async def pw_request(req: PwRequest):
    result = forgot_pw(req.email)
    token = result.pop("token", None)
    email = result.pop("email", None)
    if token and email:
        reset_url = f"https://{os.getenv('ROOT_URL')}/reset-password?token={token}"
        Emails().pw_reset_email(email, reset_url)
    return result

@router.post('/change_forgotten_pw')
async def change_forgotten_pw(req: PwForgot):
    return reset_password(req.token, req.pw)

@router.post('/change_email_request')
async def change_email_req(req: NewEmailRequest, u_id: int = Depends(get_current_user)):
    result = change_email_request(u_id, req.newEmail)
    email = result.pop("email", None)
    code = result.pop("code", None)
    if email and code:
        Emails().email_change_verification(email, code)
    return result

@router.post('/change_email')
async def change_user_emailreq(req: NewEmailChange, u_id: int = Depends(get_current_user)):
    return change_email(u_id, req.code)

@router.post('/delete_account')
async def delete_user_account(u_id: int = Depends(get_current_user)):
    sub_id = get_sub_id(u_id)
    if sub_id:
        cancel_stripe_subscription(sub_id)
    return delete_account(u_id)
