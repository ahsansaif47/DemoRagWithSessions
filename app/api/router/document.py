from fastapi import APIRouter
from app.api.handlers.document import upload_document

router = APIRouter()

# Just attach the handler
router.post("/upload")(upload_document)