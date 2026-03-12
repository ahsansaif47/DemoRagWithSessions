from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query

from app.api.handlers.document import DocumentHandlers
from app.core.dependencies.auth import get_jwt_claim
from app.core.dependencies.document import get_document_handler
from app.core.dependencies.temporal_client import get_temporal_client
from app.dto.document import UploadPDFResponseDTO
from app.utils.jwt import Claim

router = APIRouter(prefix="/documents", tags=["documents"])

# Just attach the handler
@router.post("/upload", response_model=UploadPDFResponseDTO)
async def upload(
        file: UploadFile = File(...),
        claims: Claim = Depends(get_jwt_claim),
        handler: DocumentHandlers = Depends(get_document_handler)
):
    try:
        user_id = claims.user_id
        return await handler.upload_document(user_id, file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/query")
async def search(
        query: str = Query(...),
        claims: Claim = Depends(get_jwt_claim),
        handler: DocumentHandlers = Depends(get_document_handler)
):
    try:
        user_id = claims.user_id
        return await handler.ask_question(user_id, query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{workflow_id}")
async def get_workflow_status(
        workflow_id: str,
        client=Depends(get_temporal_client)
):
    """Check the status of a document processing workflow"""
    try:
        handle = client.get_workflow_handle(workflow_id)
        result = await handle.describe()
        
        return {
            "workflow_id": workflow_id,
            "status": result.workflow_execution.status.name,
            "state": result.workflow_execution.status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))