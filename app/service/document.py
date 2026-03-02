from app.dto.document import UploadPDFRequestDTO, DocData
from app.extractor.extractor import PDFContentExtractor
from app.knowledge_unit_factory import knowledge_units
from app.models.document import DocumentTextModel, DocumentImageModel
from app.repository.document import DocumentRepository
from app.integrations.storage import local_storage
from app.core.dependencies.config import config
import logging
import uuid
from pathlib import Path
from typing import List
import os


from app.core.dependencies import database

logger = logging.getLogger(__name__)

visuals_model_path = "../../scripts/models/yolov8s-doclaynet.pt"


class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    # FIXME: Use the config variable to interact with the local and azure storage and database
    def add_document(self, user_id: str, pdf_dir: str, document: UploadPDFRequestDTO):
        try:
            # TODO: Get the user id using JWT Token
            user_id = user_id
            file_id = pdf_dir.split('/')[-1].split('.pdf')[0]


            # TODO: Load the images path using the basepath.parents technique

            base_dir = Path(__file__).resolve().parents[2]
            images_dir = base_dir / "resources" / "images"
            user_images_dir = images_dir / user_id / file_id

            # Create the user images directory using the user_id and sanitized_file_name
            # local_images_dir = config.storage.local_storage_config.images_dir
            # user_images_dir = os.path.join(local_images_dir, user_id, file_id)
            os.makedirs(user_images_dir, exist_ok=True)


            file_size_bytes = os.path.getsize(pdf_dir)

            pdf_extractor = PDFContentExtractor(pdf_path=pdf_dir)
            # TODO: Pass the user_id and file_id in this and save the file in the function
            # FIXME: Change the page_content images to have the path only. Dont save the bytes
            extracted_content = pdf_extractor.extract(user_img_dir=str(user_images_dir))

            # FIXME: Generate the file_id i.e. uuid.UUID in the service later and then pass to repo
            # TODO: file_id is required in the service layer generate it here and pass to repository layer to generate a record

            text_knowledge_units = knowledge_units.build_text_knowledge_units(extracted_content, uuid.UUID(file_id))
            image_knowledge_units = knowledge_units.build_image_knowledge_units(str(user_images_dir), uuid.UUID(file_id))

            # TODO: Wite a function in document repository to insert the image and text knowledge units in database


            doc_data = DocData()
            doc_data.file_name = document.file_name
            doc_data.file_size = file_size_bytes
            doc_data.user_id = user_id
            doc_data.file_id = str(file_id)

            document_text_model: List[DocumentTextModel] = []
            document_image_model: List[DocumentImageModel] = []
            # TODO: Convert the text knowledge units to DocumentTextModel
            for i, data in enumerate(text_knowledge_units):
                doc_txt_model = DocumentTextModel(
                    file_id=data.file_id,
                    page_number=data.page_number,
                    content=data.text,
                    embedding=data.embedding
                )
                document_text_model.append(doc_txt_model)

            # TODO: Convert the image knowledge units to DocumentImageModel
            for _, data in enumerate(image_knowledge_units):
                doc_img_model = DocumentImageModel(
                    file_id=data.file_id,
                    page_number=data.page_number,
                    image_path=data.image_path,
                    embedding=data.embedding
                )
                document_image_model.append(doc_img_model)

            # TODO: Get the images using the images get function
            self.document_repository.add_document(doc_data)
            self.document_repository.add_document_text(document_text_model)
            self.document_repository.add_document_images(document_image_model)
        except Exception as e:
            raise e

    def remove_document(self, document_id: str):
        try:
            return self.document_repository.remove_document(document_id)
        except Exception as e:
            raise e