from app.dto.document import UploadPDFRequestDTO, DocData
from app.extractor.extractor import PDFContentExtractor
from app.knowledge_unit_factory import knowledge_units
from app.models.document import DocumentTextModel, DocumentImageModel
from app.repository.document import DocumentRepository
from app.core.dependencies.config import config
import logging
import uuid
from pathlib import Path
from typing import List
import os
from app.integrations.llm.local_openai import OpenAIClient
from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService


logger = logging.getLogger(__name__)

visuals_model_path = "../../scripts/models/yolov8s-doclaynet.pt"


class DocumentService:
    def __init__(
            self,
            document_repository: DocumentRepository,
            text_embedder: E5EmbeddingService,
            image_embedder: ImageEmbeddingService,
            openai_client: OpenAIClient,
    ):
        self.document_repository = document_repository
        self.text_embedder = text_embedder
        self.image_embedder = image_embedder
        self.openai_client = openai_client

    # FIXME: Use the config variable to interact with the local and azure storage and database
    def add_document(self, user_id: str, pdf_dir: str, document: UploadPDFRequestDTO):
        try:
            user_id = user_id
            file_id = pdf_dir.split('/')[-1].split('.pdf')[0]


            base_dir = Path(__file__).resolve().parents[2]
            images_dir = base_dir / "resources" / "images"
            user_images_dir = images_dir / user_id / file_id
            os.makedirs(user_images_dir, exist_ok=True)


            file_size_bytes = os.path.getsize(pdf_dir)

            pdf_extractor = PDFContentExtractor(pdf_path=pdf_dir)
            extracted_content = pdf_extractor.extract(user_img_dir=str(user_images_dir))

            text_knowledge_units = knowledge_units.build_text_knowledge_units(extracted_content, uuid.UUID(file_id), self.text_embedder)
            image_knowledge_units = knowledge_units.build_image_knowledge_units(str(user_images_dir), uuid.UUID(file_id), self.image_embedder)

            doc_data = DocData()
            doc_data.file_name = document.file_name
            doc_data.file_size = file_size_bytes
            doc_data.user_id = user_id
            doc_data.file_id = str(file_id)

            document_text_model: List[DocumentTextModel] = []
            document_image_model: List[DocumentImageModel] = []
            for i, data in enumerate(text_knowledge_units):
                doc_txt_model = DocumentTextModel(
                    file_id=data.file_id,
                    page_number=data.page_number,
                    content=data.text,
                    embedding=data.embedding
                )
                document_text_model.append(doc_txt_model)

            for _, data in enumerate(image_knowledge_units):
                doc_img_model = DocumentImageModel(
                    file_id=data.file_id,
                    page_number=data.page_number,
                    image_path=data.image_path,
                    embedding=data.embedding
                )
                document_image_model.append(doc_img_model)

            self.document_repository.add_document(doc_data)
            self.document_repository.add_document_text(document_text_model)
            self.document_repository.add_document_images(document_image_model)
        except Exception as e:
            raise e

    def retrieve_and_answer(
            self,
            user_id: str,
            question: str,
            top_k: int = 5
    ) -> dict:

        # 1️⃣ Embed query
        query_embedding = self.text_embedder.embed_query(question, "query")

        # 2️⃣ Retrieve top-k text chunks (user-filtered)
        text_results = self.document_repository.search_similar_texts_with_pages(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=top_k
        )

        if not text_results:
            return {
                "answer": "No relevant information found.",
                "images": []
            }

        # 3️⃣ Extract page references
        file_page_pairs = [(row[0], row[1]) for row in text_results]

        # 4️⃣ Fetch images from same pages
        image_results = self.document_repository.get_images_by_pages(file_page_pairs)

        # 5️⃣ Build context
        text_context = "\n\n".join([row[2] for row in text_results])

        prompt = f"""
        Answer the question using only the context below.

        Context:
        {text_context}

        Question:
        {question}
        """

        # 6️⃣ Call LLM
        response = self.openai_client.generate_response(prompt)

        return {
            "answer": response,
            "images": [
                {
                    "file_id": row[0],
                    "page_number": row[1],
                    "image_path": row[2]
                }
                for row in image_results
            ]
        }

    def remove_document(self, document_id: str):
        try:
            return self.document_repository.remove_document(document_id)
        except Exception as e:
            raise e