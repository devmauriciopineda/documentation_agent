from controllers import process_controller
from db.pg_connection import get_db
from fastapi import APIRouter, Depends
from schemas.schemas import DocsInfo
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1", tags=["process"])


@router.post("/process-documentation")
async def process_documentation(docs_info: DocsInfo, db: Session = Depends(get_db)):
    """Endpoint to process documentation."""
    answer = process_controller.process_documents(docs_info, db)
    return {"answer": answer}


@router.get("/processing-status/{task_id}")
async def get_processing_status(task_id: str):
    """Endpoint to get processing status."""
    answer = process_controller.get_task_status(task_id)
    return answer
