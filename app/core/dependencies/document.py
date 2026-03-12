from app.api.handlers.document import DocumentHandlers
from app.repository.database import get_database_connection
from fastapi import Depends
from app.repository.document import DocumentRepository
from app.service.document import DocumentService
from app.core.dependencies.embedders import get_text_embedder, get_image_embedder
from app.core.dependencies.llm_client import get_openai_client
from app.core.dependencies.azure_storage import get_azure_storage_service
from app.core.dependencies.knowledge_units_factory import get_knowledge_units_factory
from app.core.dependencies.temporal_client import get_temporal_client

def get_document_repository(db=Depends(get_database_connection)):
    return DocumentRepository(db)


def get_document_service(
        repo=Depends(get_document_repository),
        text_embedder=Depends(get_text_embedder),
        image_embedder=Depends(get_image_embedder),
        openai_client=Depends(get_openai_client),
        azure_blob_storage=Depends(get_azure_storage_service),
        ku_factory=Depends(get_knowledge_units_factory),
        temporal_client=Depends(get_temporal_client)
):
    return DocumentService(repo, text_embedder, image_embedder, openai_client, azure_blob_storage, ku_factory, temporal_client)


def get_document_handler(service=Depends(get_document_service)):
    return DocumentHandlers(service)
