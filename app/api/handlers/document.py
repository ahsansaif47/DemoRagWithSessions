from fastapi import UploadFile, File, Depends, HTTPException
from app.service.document import DocumentService
from app.repository.document import DocumentRepository
# TODO: Replace this get_database function with get_database_connection from app.repositories.database
# from app.core.dependencies.database import get_database
from app.repository.database import get_database_connection
from app.dto.document import UploadPDFRequestDTO, UploadPDFResponseDTO
from app.core.dependencies.config import config
from app.core.dependencies.auth import get_jwt_claim
from pathlib import Path
import uuid
from app.integrations.storage import local_storage
from app.utils.jwt import Claim
import os
from app.dto.document import RemoveDocumentRequestDTO

# TODO: Import the service from the core/dependencies/document.py
# from app.core.dependencies.document import get_document_service





class DocumentHandlers:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    async def upload_document(
            self,
            user_id: str,
            file
    ) -> UploadPDFResponseDTO:
        # Generate file ID
        file_id = str(uuid.uuid4())

        base_dir = Path(__file__).resolve().parents[3]
        pdf_dir = base_dir / "resources" / "pdf"
        user_dir = pdf_dir / user_id

        user_dir.mkdir(parents=True, exist_ok=True)

        # # Build storage path
        # base_dir = config.storage.local_storage_config.pdf_dir
        # user_dir = os.path.join(base_dir, user_id)
        # os.makedirs(user_dir, exist_ok=True)

        file_path = os.path.join(str(user_dir), f"{file_id}.pdf")

        # Save uploaded file
        # TODO: Call the save file from the integrations/storage package to save in chunks for faster uploads
        await local_storage.store_file_chunks(file, file_path)
        # with open(file_path, "wb") as buffer:
        #     buffer.write(await file.read())

        # Prepare DTO
        dto = UploadPDFRequestDTO()
        dto.file_name = file.filename
        dto.file_path = file_path

        # Call service
        self.document_service.add_document(user_id=user_id, pdf_dir=file_path, document=dto)
        res = UploadPDFResponseDTO(
            message="Document uploaded successfully",
            status="201",
            file_id=file_id
        )

        return res

    def remove_document(self, req: RemoveDocumentRequestDTO):
        return self.document_service.remove_document(req.document_id)



# TODO: Move this from here to the documents dependency in core/dependencies/document.py
# TODO: Then import this function here
# def get_document_service():
#     repo = DocumentRepository(get_database_connection)
#     return DocumentService(repo)


# async def upload_document(
#     file: UploadFile = File(...),
#     claims:Claim = Depends(get_jwt_claim),
#     service: DocumentService = Depends(get_document_service),
# ):
#     try:
#         user_id = claims.user_id
#
#         # Generate file ID
#         file_id = str(uuid.uuid4())
#
#
#         base_dir = Path(__file__).resolve().parents[3]
#         pdf_dir = base_dir / "resources" / "pdf"
#         user_dir = pdf_dir / user_id
#
#         user_dir.mkdir(parents=True, exist_ok=True)
#
#
#         # # Build storage path
#         # base_dir = config.storage.local_storage_config.pdf_dir
#         # user_dir = os.path.join(base_dir, user_id)
#         # os.makedirs(user_dir, exist_ok=True)
#
#         file_path = os.path.join(str(user_dir), f"{file_id}.pdf")
#
#         # Save uploaded file
#         # TODO: Call the save file from the integrations/storage package to save in chunks for faster uploads
#         await local_storage.store_file_chunks(file, file_path)
#         # with open(file_path, "wb") as buffer:
#         #     buffer.write(await file.read())
#
#         # Prepare DTO
#         dto = UploadPDFRequestDTO()
#         dto.file_name = file.filename
#         dto.file_path = file_path
#
#         # Call service
#         service.add_document(user_id=user_id, pdf_dir=file_path, document=dto)
#
#         return {"message": "Document uploaded successfully", "file_id": file_id}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))