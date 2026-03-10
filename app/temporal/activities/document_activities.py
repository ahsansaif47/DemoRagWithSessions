from temporalio import activity
from app.extractor.extractor import PDFContentExtractor
from app.repository.document import DocumentRepository
from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.knowledge_unit_factory.knowledge_units import KnowledgeUnitsFactory
from app.models.document import DocumentTextModel, DocumentImageModel
from app.extractor.content import ExtractedContent
from typing import List
import uuid


class DocumentActivities:
    def __init__(
            self,
            extractor: PDFContentExtractor,
            repo: DocumentRepository,
            storage: AzureStorageService,
            ku_factory: KnowledgeUnitsFactory
    ):
        self.extractor = extractor
        self.repo = repo
        self.storage = storage
        self.ku_factory = ku_factory

    @activity.defn
    async def extract(self, images_dir: str):
        content = self.extractor.extract(images_dir, self.storage)
        return content

    @activity.defn
    async def process_text_knowledge_units(self, file_id: str, content: ExtractedContent):
        text_knowledge_units = self.ku_factory.build_text_knowledge_units(content, uuid.UUID(file_id))

        document_text_models: List[DocumentTextModel] = []
        for i, data in enumerate(text_knowledge_units):
            doc_txt_model = DocumentTextModel(
                file_id=data.file_id,
                page_number=data.page_number,
                content=data.text,
                embedding=data.embedding
            )
            document_text_models.append(doc_txt_model)

        self.repo.add_document_text(document_text_models)

    async def process_image_knowledge_units(self, user_book_images_dir: str, file_id: str):
        image_knowledge_units = self.ku_factory.build_image_knowledge_units(user_book_images_dir, uuid.UUID(file_id))

        document_image_models: List[DocumentImageModel] = []
        for _, data in enumerate(image_knowledge_units):
            doc_img_model = DocumentImageModel(
                file_id=data.file_id,
                page_number=data.page_number,
                image_path=data.image_path,
                embedding=data.embedding
            )
            document_image_models.append(doc_img_model)
        self.repo.add_document_images(document_image_models)
