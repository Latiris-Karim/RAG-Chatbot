from fastapi import APIRouter, Depends, HTTPException
from src.services.rag_service import RAG
import src.db.chat_db as chat_db
from src.utils.jwt_handler import get_current_user
from pydantic import BaseModel
import src.db.subscription_db as subscription_db
import src.db.free_pro_db as free_pro_db
import time

router = APIRouter(prefix="/chat", tags=["chat"])

class message(BaseModel):
   txt: str 
   chatroom_id: int

@router.post("/create/chatroom")
async def create_chatroom(u_id: int = Depends(get_current_user)):
    return chat_db.create_chatroom(u_id)

@router.post("/send")
async def send_message(req: message, u_id: int = Depends(get_current_user)):
   if not subscription_db.has_active_subscription(u_id) and free_pro_db.is_user_at_limit(u_id):
      timeleft = free_pro_db.get_time_until_reset()
      return {'message': f'You can use the chat in {timeleft:.1f} hours again!'}
   
   if not subscription_db.has_active_subscription(u_id):
        free_pro_db.increase_query_counter(u_id)

   t1= time.time()
   rag = RAG()
   chat_db.save_msg(req.txt, req.chatroom_id, u_id, role='user')
   res = await rag.pipeline(req.txt)
   chat_db.save_msg(res, req.chatroom_id, u_id, role='ai')
   t2 = time.time()
   print(f"respone time:{t2-t1:.2f}s")
   return res

@router.get("/get_chatrooms")
async def get_chatrooms(u_id: int = Depends(get_current_user)):
   res = chat_db.get_chatrooms(u_id)
   return res

@router.get("/get_msgs")
async def get_msgs(chatroom_id, u_id: int = Depends(get_current_user)):
   if chat_db.access_to_chatroom(chatroom_id, u_id):
      res = chat_db.get_chatroom_msgs(chatroom_id)
      return res
   else:
      raise HTTPException(status_code=403, detail="Chatroom access denied or Chatroom doesnt exist")
