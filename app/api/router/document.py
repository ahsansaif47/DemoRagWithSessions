from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from sqlalchemy.util import await_only

from app.api.handlers.document import DocumentHandlers
from app.dto.document import UploadPDFResponseDTO
from app.core.dependencies.document import get_document_handler
from app.utils.jwt import Claim
from app.core.dependencies.auth import get_jwt_claim


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