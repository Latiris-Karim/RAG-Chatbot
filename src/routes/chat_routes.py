from fastapi import APIRouter, Depends
from src.services.rag_service import RAG
import src.db.chat_db as chat_db
from src.utils.jwt_handler import get_current_user
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/send")#also store this + return in db
async def send_message(txt: str):
    rag = RAG()
    return await rag.pipeline(txt)

@router.post("/create/chatroom")
async def create_chatroom(chatroom_id: int, u_id: int = Depends(get_current_user)):
    return await chat_db.create_chatroom(chatroom_id, u_id)
