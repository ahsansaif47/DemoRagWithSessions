from app.dto.document import UploadPDFRequestDTO, DocData
from app.extractor.extractor import PDFContentExtractor
from app.knowledge_unit_factory import knowledge_units
from app.repository.document import DocumentRepository
from app.integrations.storage import local_storage
from app.core.dependencies.config import config
import logging
import uuid
import os


from app.core.dependencies import database

logger = logging.getLogger(__name__)

visuals_model_path = "../../scripts/models/yolov8s-doclaynet.pt"


class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    # FIXME: Use the config variable to interact with the local and azure storage and database
    def add_document(self, user_id: str, document: UploadPDFRequestDTO):
        try:
            # TODO: Get the user id using JWT Token
            user_id = user_id
            file_id = uuid.uuid4()
            file_id_str = str(file_id)



            # NOTE: Check if this might be done in the handlers layer
            # Create the user document directory using the user_id
            # No need to create the directory ending with file name else every book directory will just have one single PDF
            local_pdf_dir = config.storage.local_storage_config.pdf_dir
            user_pdf_dir = os.path.join(local_pdf_dir, user_id)
            # os.makedirs(user_pdf_dir, exist_ok=True)


            # Create the user images directory using the user_id and sanitized_file_name
            local_images_dir = config.storage.local_storage_config.images_dir
            user_images_dir = os.path.join(local_images_dir, user_id, file_id_str)
            os.makedirs(user_images_dir, exist_ok=True)


            user_pdf_file = os.path.join(user_pdf_dir, file_id_str+".pdf")
            file_size_bytes = os.path.getsize(user_pdf_file)

            pdf_extractor = PDFContentExtractor(user_pdf_dir)
            extracted_content = pdf_extractor.extract()

            # FIXME: Generate the file_id i.e. uuid.UUID in the service later and then pass to repo
            # TODO: file_id is required in the service layer generate it here and pass to repository layer to generate a record

            text_knowledge_units = knowledge_units.build_text_knowledge_units(extracted_content, file_id)

            # TODO: Get the path using the user_id and sanitized_file_name to navigate to user uploaded book images
            # And call the image knowledge units code over here
            for pg_content in extracted_content.page_content:
                images = pg_content.images
                for img in images:
                    img_save_path = os.path.join(user_images_dir, img.image_name)
                    local_storage.save_image(img_save_path, img.image_data)

            image_knowledge_units = knowledge_units.build_image_knowledge_units(user_images_dir, file_id)

            # TODO: Wite a function in document repository to insert the image and text knowledge units in database


            doc_data = DocData()
            doc_data.file_name = document.file_name
            doc_data.file_size = file_size_bytes
            doc_data.user_id = user_id
            doc_data.file_id = str(file_id.bytes)


            # TODO: Get the images using the images get function
            self.document_repository.add_document(doc_data)
        except Exception as e:
            raise e

    def remove_document(self, document_id: str):
        try:
            return self.document_repository.remove_document(document_id)
        except Exception as e:
            raise e