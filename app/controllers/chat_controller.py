from models.chat import Chat, Message
from sqlalchemy.orm import Session
from workflows.graph import compiled_graph


def query_documents(chat_id: str, message: str, db: Session):
    """Function to query documents based on the chat ID and message."""
    result = compiled_graph.invoke(
        {
            "question": message,
            "chat_id": chat_id,
            "documents": [],
            "intent": None,
            "answer": None,
            "code": None,
            "messages": [],
        }
    )
    answer = result.get('answer')
    save_message(chat_id, {"role": "user", "content": message}, db)
    save_message(chat_id, {"role": "assistant", "content": answer}, db)
    return answer


def get_chat_history(chat_id: str, db: Session):
    """Function to get the chat history based on the chat ID."""
    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .all()
    )
    return messages


def create_chat(chat_id: str, url: str, db: Session):
    """Function to create a new chat."""
    new_chat = Chat(id=chat_id, url=url)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


def save_message(chat_id: str, message: dict, db: Session):
    """Function to save a message to the database."""
    new_message = Message(
        chat_id=chat_id, role=message.get('role'), content=message.get('content')
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message
