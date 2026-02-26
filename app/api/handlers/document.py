from fastapi import UploadFile, File, Depends, HTTPException
from app.service.document import DocumentService
from app.repository.document import DocumentRepository
# TODO: Replace this get_database function with get_database_connection from app.repositories.database
from app.core.dependencies.database import get_database
from app.dto.document import UploadPDFRequestDTO
from app.core.dependencies.config import config
from app.core.dependencies.auth import get_jwt_claim
import uuid
import os


def get_document_service():
    repo = DocumentRepository(get_database())
    return DocumentService(repo)


async def upload_document(
    file: UploadFile = File(...),
    claims:dict = Depends(get_jwt_claim),
    service: DocumentService = Depends(get_document_service),
):
    try:
        user_id = claims["user_id"]

        # Generate file ID
        file_id = str(uuid.uuid4())

        # Build storage path
        base_dir = config.storage.local_storage_config.pdf_dir
        user_dir = os.path.join(base_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)

        file_path = os.path.join(str(user_dir), f"{file_id}.pdf")

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Prepare DTO
        dto = UploadPDFRequestDTO()
        dto.file_name = file.filename
        dto.file_path = file_path

        # Call service
        service.add_document(user_id=user_id, document=dto)

        return {"message": "Document uploaded successfully", "file_id": file_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))