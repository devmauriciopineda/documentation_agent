from celery.result import AsyncResult
from schemas.schemas import DocsInfo
from celery import states

from celery_tasks.tasks import process_documentation_task
from celery_tasks.worker import app


def process_documents(docs_info: DocsInfo):
    """Function to process documentation."""
    task_id = process_documentation_task.delay(docs_info.url, docs_info.chatId)
    id = task_id.id
    return {"task_id": id, "status": str(states.PENDING)}


def get_task_status(task_id: str):
    """Function to get task status."""
    result = app.AsyncResult(task_id)
    return {"task_id": task_id, "status": str(result.state)}
