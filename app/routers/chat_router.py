from fastapi import APIRouter, Depends
from db.pg_connection import get_db
from sqlalchemy.orm import Session
from schemas.schemas import Message
from controllers import chat_controller

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat/{chatId}")
async def send_message(chatId: str, msg: Message, db: Session = Depends(get_db)):
    """
    Endpoint to send a message to a chat.
    """
    answer = chat_controller.query_documents(chatId, msg.message, db)
    return {"chat_id": chatId, "message": answer}


@router.get("/chat-history/{chatId}")
async def get_chat_history(chatId: str, db: Session = Depends(get_db)):
    """
    Endpoint to get the chat history.
    """
    messages = chat_controller.get_chat_history(chatId, db)
    return {"chat_id": chatId, "messages": messages}

