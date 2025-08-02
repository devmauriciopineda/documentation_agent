from models.chat import Chat, Message
from sqlalchemy.orm import Session


def query_documents(chat_id: str, message: str, db: Session):
    """
    Function to query documents based on the chat ID and message.
    """
    return None  # Placeholder for actual implementation


def get_chat_history(chat_id: str, db: Session):
    """
    Function to get the chat history based on the chat ID.
    """
    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at)
        .desc()
        .all()
    )
    return messages
