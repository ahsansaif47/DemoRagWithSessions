

class UploadPDFRequestDTO:
    file_name: str
    file_bytes: bytes

class UploadPDFResponseDTO:
    file_id: str
    status: str
    message: str

class DocData:
    user_id: str
    file_name: str
    file_size: int
