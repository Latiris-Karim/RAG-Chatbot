from fastapi import APIRouter, Depends
from src.services.rag_service import RAG#runs all module code but only gives access to the class
import src.db.chat_db as chat_db
from src.utils.jwt_handler import get_current_user
import time

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/create/chatroom")
async def create_chatroom(chatroom_id: int, u_id: int = Depends(get_current_user)):
    return chat_db.create_chatroom(chatroom_id, u_id)

@router.post("/send")
async def send_message(txt: str, chatroom_id: int, u_id: int = Depends(get_current_user)):
   t1= time.time()
   rag = RAG()
   chat_db.save_msg(txt, chatroom_id, u_id, role='user')
   res = await rag.pipeline(txt)
   chat_db.save_msg(res, chatroom_id, u_id, role='ai')
   t2 = time.time()
   print(f"respone time:{t2-t1:.2f}s")
   return res

@router.get("/get_chatrooms")
async def get_chatrooms(u_id: int = Depends(get_current_user)):
   res = chat_db.get_chatrooms(u_id)
   return res

@router.get("/get_msgs")
async def get_msgs(chatroom_id, u_id: int = Depends(get_current_user)):
   res = chat_db.get_chatroom_msgs(chatroom_id, u_id)
   return res
