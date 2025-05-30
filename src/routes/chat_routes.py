from fastapi import APIRouter, Depends
from src.services.rag_service import RAG
import src.db.chat_db as chat_db
from src.utils.jwt_handler import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/create/chatroom")
async def create_chatroom(chatroom_id: int, u_id: int = Depends(get_current_user)):
    return chat_db.create_chatroom(chatroom_id, u_id)

@router.post("/send")
async def send_message(txt: str, chatroom_id: int, u_id: int = Depends(get_current_user)):
  rag = RAG()
  chat_db.save_msg(txt, chatroom_id, u_id, role='user')
  res = await rag.pipeline(txt)
  chat_db.save_msg(res, chatroom_id, u_id, role='ai')
  return res
