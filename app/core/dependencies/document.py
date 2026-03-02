from app.api.handlers.document import DocumentHandlers
from app.repository.database import get_database_connection
from fastapi import Depends
from app.repository.document import DocumentRepository
from app.service.document import DocumentService


def get_document_repository(db=Depends(get_database_connection)):
    return DocumentRepository(db)


def get_document_service(repo=Depends(get_document_repository)):
    return DocumentService(repo)


def get_document_handler(service=Depends(get_document_service)):
    return DocumentHandlers(service)
