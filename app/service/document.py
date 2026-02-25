import logging
import os
from app.repository.document import DocumentRepository
from app.pdf_extractor.text_extractor import TextExtractor
from app.pdf_extractor.image_extractor import extract_visual_elements
from app.dto.document import UploadPDFRequestDTO, DocData

from app.core.dependencies.config import config

logger = logging.getLogger(__name__)

visuals_model_path = "../../scripts/models/yolov8s-doclaynet.pt"

class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    def add_document(self, user_id: str, document: UploadPDFRequestDTO):
        try:
            # TODO: Get the user id using JWT Token
            user_id = user_id


            local_pdf_dir = config.storage.local_storage
            user_pdf_dir = os.path.join(local_pdf_dir, user_id)

            os.makedirs(user_pdf_dir, exist_ok=True)
            # TODO: Call the file chunk save from the

            # TODO: Get the local path from the config

            # Get the absolute file path from the users PDF directory
            user_file = os.path.join(user_pdf_dir, document.file_name)
            file_size_bytes = os.path.getsize(user_file)
            txt_extractor = TextExtractor(document.file_name, user_file)


            doc_data = DocData()
            doc_data.file_name = document.file_name
            doc_data.file_size = file_size_bytes
            doc_data.user_id = user_id

            # TODO: Get the images directory from the config
            extract_visual_elements(user_pdf_dir, visuals_model_path, config.storage.local_storage)


            # Get the textual content from the text extractor
            content = txt_extractor.extract_text()
            for idx, data in enumerate(content.page_content):
                for _, element in enumerate(data.images):
                    # TODO: Generate the text embeddings here
                    pass

            # TODO: Get the images using the images get function
            self.document_repository.add_document(doc_data)
            # TODO: Enrich the textual content with the images in it.

            '''
                Steps:
                1. Load the documents directory from the config.
                2. Check if the user documents directory exists?
                3. If exists, navigate to users documents directory.
                4. Pick the file from user's documents directory.
                5. Extract images/text.
                6. Generate embeddings.
                7. Save to postgres. 
            '''



            # Load from the config the general document directory path then do {documents_direc}/
            # TODO: Use the text and image extractor to get the data from pdf document
            pass
        except Exception as e:
            raise e

    def remove_document(self, document_id: str):
        try:
            return self.document_repository.remove_document(document_id)
        except Exception as e:
            raise e
