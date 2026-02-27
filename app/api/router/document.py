from fastapi import APIRouter
from app.api.handlers.document import upload_document

router = APIRouter(prefix="/documents", tags=["documents"])

# Just attach the handler
router.post("/upload")(upload_document)