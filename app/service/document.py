import logging
from app.repository.document import DocumentRepository
from app.pdf_extractor import image_extractor, text_extractor

logger = logging.getLogger(__name__)



class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    def add_document(self):
        try:
            # TODO: Use the text and image extractor to get the data from pdf document
            pass
        except Exception as e:
            raise e

    def remove_document(self):
        try:
            pass
        except Exception as e:
            raise e
