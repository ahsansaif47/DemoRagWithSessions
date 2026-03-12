import logging
import uuid
from pathlib import Path
from typing import List, Optional

from app.dto.document import UploadPDFRequestDTO, DocData
from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService
from app.integrations.llm.local_openai import OpenAIClient
from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.knowledge_unit_factory.knowledge_units import KnowledgeUnitsFactory
from app.repository.document import DocumentRepository

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
            self,
            document_repository: DocumentRepository,
            text_embedder: E5EmbeddingService,
            image_embedder: ImageEmbeddingService,
            openai_client: OpenAIClient,
            azure_blob_storage: AzureStorageService,
            ku_factory: KnowledgeUnitsFactory,
            temporal_client: Optional = None
    ):
        self.document_repository = document_repository
        self.text_embedder = text_embedder
        self.image_embedder = image_embedder
        self.openai_client = openai_client
        self.azure_blob_storage = azure_blob_storage
        self.ku_factory = ku_factory
        self.temporal_client = temporal_client

    async def add_document(self, user_id: str, pdf_dir: str, document: UploadPDFRequestDTO):
        """
        Start a Temporal workflow to process document ingestion asynchronously.
        
        Returns the workflow ID for tracking the ingestion process.
        """
        try:
            # Extract file_id from path
            file_id = pdf_dir.split('/')[-1].split('.pdf')[0]
            
            if not self.temporal_client:
                raise ValueError("Temporal client not initialized. Cannot start workflow.")
            
            # Start the Temporal workflow
            from app.temporal.workflows.document_workflows import DocumentIngestionWorkflow
            
            # result = await self.temporal_client.start_workflow(
            #     DocumentIngestionWorkflow.run,
            #     pdf_dir,
            #     user_id,
            #     file_id,
            #     document.file_name,
            #     id=f"document-ingestion-{file_id}",
            #     task_queue="document-task-queue"
            # )

            result = await self.temporal_client.start_workflow(
                DocumentIngestionWorkflow.run,  # Best practice to reference the run method
                args=[pdf_dir, user_id, file_id, document.file_name],
                id=f"document-ingestion-{file_id}",
                task_queue="document-task-queue"
            )
            
            logger.info(f"Started document ingestion workflow: {result.id}")
            
            return {
                "workflow_id": result.id,
                "file_id": file_id,
                "status": "processing"
            }
            
        except Exception as e:
            logger.error(f"Error starting document ingestion workflow: {str(e)}")
            raise e

    def retrieve_and_answer(
            self,
            user_id: str,
            question: str,
            top_k: int = 5
    ) -> dict:
        """
        Synchronous query processing - kept in service layer for fast response.
        """

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
        """
        Synchronous document removal - kept in service layer for fast execution.
        """
        try:
            return self.document_repository.remove_document(document_id)
        except Exception as e:
            logger.error(f"Error removing document: {str(e)}")
            raise e