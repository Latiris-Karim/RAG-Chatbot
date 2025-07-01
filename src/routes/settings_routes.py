from fastapi import APIRouter, Depends
from src.utils.jwt_handler import get_current_user
from pydantic import BaseModel
from src.db.settings_db import change_pw, user_info, reset_password, forgot_pw, delete_account, change_email, change_email_request

router = APIRouter(prefix="/settings", tags=["settings"])

class PwChange(BaseModel):
    password: str

class PwForgot(BaseModel):
    token: str
    password: str

class PwRequest(BaseModel):
    email: str

class NewEmailRequest(BaseModel):
    newEmail: str

class NewEmailChange(BaseModel):
    code: str

@router.get('/display')
async def display(u_id: int = Depends(get_current_user)):
    res = user_info(u_id)
    return res

@router.post('/change_pw')#from logged in user
async def change_current_pw(req: PwChange, u_id: int = Depends(get_current_user)):
    return change_pw(u_id, req.password)

@router.post('/request_pw_change')#send url for pw change to user-email
async def pw_request(req: PwRequest):
    email = req.email
    return forgot_pw(email)

@router.post('/change_forgotten_pw')#validate token in url then change pw 
async def change_forgotten_pw(req: PwForgot):
    reset_token = req.token
    new_pw = req.password
    return reset_password(reset_token, new_pw)

@router.post('/delete_account')
async def delete_user_account(u_id: int = Depends(get_current_user)):
    res = delete_account(u_id)
    return res

@router.post('/change_email_request')
async def change_email_req(req: NewEmailRequest,u_id: int = Depends(get_current_user)):
    res = change_email_request(u_id,req.newEmail)
    return res


@router.post('/change_email')
async def change_user_emailreq(req: NewEmailChange, u_id:int = Depends(get_current_user)):
    res = change_email(u_id, req.code)
    return res
