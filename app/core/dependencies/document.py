from app.api.handlers.document import DocumentHandlers
from app.repository.database import get_database_connection
from fastapi import Depends
from app.repository.document import DocumentRepository
from app.service.document import DocumentService
from app.core.dependencies.embedders import get_text_embedder, get_image_embedder
from app.core.dependencies.llm_client import get_openai_client

def get_document_repository(db=Depends(get_database_connection)):
    return DocumentRepository(db)


def get_document_service(
        repo=Depends(get_document_repository),
        text_embedder=Depends(get_text_embedder),
        image_embedder=Depends(get_image_embedder),
        openai_client=Depends(get_openai_client)
):
    return DocumentService(repo, text_embedder, image_embedder, openai_client)


def get_document_handler(service=Depends(get_document_service)):
    return DocumentHandlers(service)
