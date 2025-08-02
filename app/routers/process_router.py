from fastapi import APIRouter
from schemas.schemas import DocsInfo

router = APIRouter(prefix="/api/v1", tags=["process"])


@router.post("/process-documentation")
async def process_documentation(docs_info: DocsInfo):
    """
    Endpoint to process documentation.
    """
    return {"message": "Documentation processed successfully."}


@router.get("/processing-status/{chatId}")
async def get_processing_status(chatId: str):
    """
    Endpoint to get processing status.
    """
    return {"status": "processing"}
