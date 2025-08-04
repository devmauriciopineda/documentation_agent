import uuid

from celery import states
from celery.result import AsyncResult
from celery_tasks.tasks import process_documentation_task
from celery_tasks.worker import app
from controllers.chat_controller import create_chat
from schemas.schemas import DocsInfo
from sqlalchemy.orm import Session


def process_documents(docs_info: DocsInfo, db: Session):
    """Function to process documentation."""
    chat_id = docs_info.chatId
    if not chat_id:
        chat_id = str(uuid.uuid4())
        chat_in_db = create_chat(chat_id, docs_info.url, db)
    task_id = process_documentation_task.delay(docs_info.url, chat_id)
    id = task_id.id
    return {"task_id": id, "chat_id": chat_id, "status": str(states.PENDING)}


def get_task_status(task_id: str):
    """Function to get task status."""
    result = app.AsyncResult(task_id)
    return {"task_id": task_id, "status": str(result.state)}
