import uuid
from pydantic import BaseModel

class UploadPDFRequestDTO:
    file_name: str
    file_path: str  # Set this value after saving the file to path

class UploadPDFResponseDTO(BaseModel):
    file_id: str
    status: str
    message: str

class DocData:
    user_id: str
    file_id: str
    file_name: str
    file_size: int


class RemoveDocumentRequestDTO:
    document_id: str

