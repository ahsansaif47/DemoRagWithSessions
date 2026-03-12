import datetime
from datetime import timedelta, timezone
from typing import Optional

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.temporal.activities.document_activities import DocumentActivities


@workflow.defn
class DocumentIngestionWorkflow:
    """Workflow for ingesting PDF documents into the RAG system"""
    
    @workflow.run
    async def run(self, pdf_path: str, user_id: str, file_id: str, file_name: str) -> str:
        """
        Execute the document ingestion workflow
        
        Args:
            pdf_path: Path to the PDF file
            user_id: User ID who owns the document
            file_id: Unique file identifier
            file_name: Original filename
            
        Returns:
            file_id: The ID of the ingested document
        """

        # FIXME: Save the data to path and return the path and get the path in next activity if required
        
        # Define retry policy for activities
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
            backoff_coefficient=2.0,
        )
        
        # Step 1: Upload PDF to Azure Blob Storage
        upload_result = await workflow.execute_activity(
            DocumentActivities.upload_pdf_to_azure,
            args=[pdf_path, user_id, file_id],
            start_to_close_timeout=timedelta(seconds=300),
            retry_policy=retry_policy
        )

        # Step 2: Extract PDF content (text and images)
        extraction_result = await workflow.execute_activity(
            DocumentActivities.extract_pdf_content,
            args=[pdf_path, user_id, file_id],
            start_to_close_timeout=timedelta(minutes=50),
            retry_policy=retry_policy
        )

        # TODO: Remove this from the workflow and get the content from the path
        extracted_content = extraction_result["extracted_content_file"]
        user_images_dir = extraction_result["user_images_dir"]
        user_id = extraction_result["user_id"]

        # Step 3: Process text embeddings
        text_models_path = await workflow.execute_activity(
            DocumentActivities.process_text_embeddings,
            args=[file_id, extracted_content, user_id],
            start_to_close_timeout=timedelta(minutes=50),
            retry_policy=retry_policy
        )

        # Step 4: Process image embeddings
        image_models_path = await workflow.execute_activity(
            DocumentActivities.process_image_embeddings,
            args=[file_id, user_images_dir, user_id],
            start_to_close_timeout=timedelta(minutes=50),
            retry_policy=retry_policy
        )

        # Step 5: Store document metadata
        await workflow.execute_activity(
            DocumentActivities.store_document_metadata,
            args=[user_id, file_id, file_name, upload_result["file_size_bytes"]],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=retry_policy
        )

        # Step 6: Store text embeddings (can run in parallel with image embeddings storage)
        text_count = await workflow.execute_activity(
            DocumentActivities.store_text_embeddings,
            args=[text_models_path],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )

        # Step 7: Store image embeddings
        image_count = await workflow.execute_activity(
            DocumentActivities.store_image_embeddings,
            args=[image_models_path],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )
        
        workflow.logger.info(
            f"Document ingestion completed: {file_id}, "
            f"text_chunks: {text_count}, images: {image_count}"
        )
        
        return file_id