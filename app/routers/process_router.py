from fastapi import APIRouter
from schemas.schemas import DocsInfo
from controllers import process_controller

router = APIRouter(prefix="/api/v1", tags=["process"])


@router.post("/process-documentation")
async def process_documentation(docs_info: DocsInfo):
    """
    Endpoint to process documentation.
    """
    answer = process_controller.process_documents(docs_info)
    return {"answer": answer}


@router.get("/processing-status/{task_id}")
async def get_processing_status(task_id: str):
    """
    Endpoint to get processing status.
    """
    answer = process_controller.get_task_status(task_id)
    return answer
