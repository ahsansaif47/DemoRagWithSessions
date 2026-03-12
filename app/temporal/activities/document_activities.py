import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
from temporalio import activity
import pickle

from app.extractor.extractor import PDFContentExtractor
from app.repository.document import DocumentRepository
from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.knowledge_unit_factory.knowledge_units import KnowledgeUnitsFactory
from app.models.document import DocumentTextModel, DocumentImageModel
from app.extractor.content import ExtractedContent
from app.dto.document import DocData


class DocumentActivities:
    def __init__(
            self,
            repo: DocumentRepository,
            storage: AzureStorageService,
            ku_factory: KnowledgeUnitsFactory
    ):
        self.repo = repo
        self.storage = storage
        self.ku_factory = ku_factory

    @activity.defn
    async def upload_pdf_to_azure(self, pdf_path: str, user_id: str, file_id: str) -> Dict[str, Any]:
        """Upload PDF file to Azure Blob Storage"""
        pdf_blob_name = f'{user_id}/{file_id}.pdf'
        self.storage.upload_file(file_path=pdf_path, blob_name=pdf_blob_name, file_type="pdf")
        
        file_size_bytes = os.path.getsize(pdf_path)
        
        return {
            "pdf_blob_name": pdf_blob_name,
            "file_size_bytes": file_size_bytes
        }

    @activity.defn
    async def extract_pdf_content(self, pdf_path: str, user_id: str, file_id: str) -> Dict[str, Any]:
        """Extract text and images from PDF"""
        base_dir = Path(__file__).resolve().parents[3]
        images_dir = base_dir / "resources" / "images"
        user_images_dir = images_dir / user_id / file_id
        os.makedirs(user_images_dir, exist_ok=True)

        pdf_extractor = PDFContentExtractor(pdf_path=pdf_path)
        extracted_content = pdf_extractor.extract(user_img_dir=str(user_images_dir), azure_storage=self.storage)


        # TODO: Save the extracted content to file
        temporal_file_obj = base_dir / "resources" /"temporal" / user_id
        file_path = str(temporal_file_obj) + f"/{file_id}_pdf_content.pkl"
        os.makedirs(temporal_file_obj, exist_ok=True)

        with open(file_path, 'wb') as file:
            pickle.dump(extracted_content, file)


        return {
            # "extracted_content": extracted_content,
            "extracted_content_file": file_path,
            "user_images_dir": str(user_images_dir),
            "user_id": user_id
        }

    @activity.defn
    async def process_text_embeddings(self, file_id: str, content_path: str, user_id: str) -> str:
        """Generate text knowledge units with embeddings"""

        # TODO: Get the data from the path
        extracted_content = None
        with open(content_path, 'rb') as file:
            extracted_content = pickle.load(file)

        text_knowledge_units = self.ku_factory.build_text_knowledge_units(extracted_content, uuid.UUID(file_id))

        document_text_models: List[DocumentTextModel] = []
        for data in text_knowledge_units:
            doc_txt_model = DocumentTextModel(
                file_id=str(data.file_id),
                page_number=data.page_number,
                content=data.text,
                embedding=data.embedding
            )
            document_text_models.append(doc_txt_model)

        base_dir = Path(__file__).resolve().parents[3]
        temporal_file_obj = base_dir / "resources" / "temporal" / user_id
        file_path = str(temporal_file_obj) + f"/{file_id}_text_embeddings.pkl"
        os.makedirs(temporal_file_obj, exist_ok=True)

        with open(file_path, 'wb') as file:
            pickle.dump(document_text_models, file)

        return file_path

    @activity.defn
    async def process_image_embeddings(self, file_id: str, user_images_dir: str, user_id: str) -> str:
        """Generate image knowledge units with embeddings"""
        image_knowledge_units = self.ku_factory.build_image_knowledge_units(user_images_dir, uuid.UUID(file_id))

        document_image_models: List[DocumentImageModel] = []
        for data in image_knowledge_units:
            doc_img_model = DocumentImageModel(
                file_id=str(data.file_id),
                page_number=data.page_number,
                image_path=data.image_path,
                embedding=data.embedding
            )
            document_image_models.append(doc_img_model)

        base_dir = Path(__file__).resolve().parents[3]
        temporal_file_obj = base_dir / "resources" / "temporal" / user_id
        file_path = str(temporal_file_obj) + f"/{file_id}_image_embeddings.pkl"
        os.makedirs(temporal_file_obj, exist_ok=True)

        with open(file_path, 'wb') as file:
            pickle.dump(document_image_models, file)
        
        return file_path

    @activity.defn
    async def store_document_metadata(self, user_id: str, file_id: str, file_name: str, file_size: int) -> str:
        """Store document metadata in database"""
        doc_data = DocData()
        doc_data.file_name = file_name
        doc_data.file_size = file_size
        doc_data.user_id = user_id
        doc_data.file_id = file_id

        self.repo.add_document(doc_data)
        return file_id

    @activity.defn
    async def store_text_embeddings(self, document_text_models_path: str) -> int:
        """Batch insert text embeddings into database"""

        text_embeddings = None
        with open(document_text_models_path, 'rb') as file:
            text_embeddings = pickle.load(file)


        self.repo.add_document_text(text_embeddings)
        return len(text_embeddings)

    @activity.defn
    async def store_image_embeddings(self, document_image_models_path: str) -> int:
        """Batch insert image embeddings into database"""

        image_embeddings = None
        with open(document_image_models_path, 'rb') as file:
            image_embeddings = pickle.load(file)

        self.repo.add_document_images(image_embeddings)
        return len(image_embeddings)
