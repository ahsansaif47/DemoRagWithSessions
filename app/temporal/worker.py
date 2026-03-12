import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from app.integrations.embeddings.local_openai import ImageEmbeddingService, E5EmbeddingService
from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.knowledge_unit_factory.knowledge_units import KnowledgeUnitsFactory
from app.repository.document import DocumentRepository
from app.repository.database import get_database_connection, PostgresPool
from app.core.dependencies.azure_storage import init_azure_storage_service
from app.core.dependencies.embedders import init_text_embedder, init_image_embedder
from app.core.dependencies.knowledge_units_factory import init_knowledge_unit_factory
from app.temporal.activities.document_activities import DocumentActivities
from app.temporal.workflows.document_workflows import DocumentIngestionWorkflow


logger = logging.getLogger(__name__)


async def start_worker(
        client: Client,
        storage: AzureStorageService,
        ku_factory: KnowledgeUnitsFactory
):
    """Start the Temporal worker for document processing"""
    
    # Connect to Temporal server
    # client = await Client.connect("localhost:7233")
    logger.info("Connected to Temporal server")

    # Initialize dependencies
    pool = PostgresPool.get_local_pool()
    repo = DocumentRepository(pool)

    logger.info("Dependencies initialized")

    # Create activities instance
    activities = DocumentActivities(
        repo=repo,
        storage=storage,
        ku_factory=ku_factory
    )
    
    # Create worker with activities and workflows
    worker = Worker(
        client=client,
        task_queue="document-task-queue",
        workflows=[DocumentIngestionWorkflow],
        activities=[
            activities.upload_pdf_to_azure,
            activities.extract_pdf_content,
            activities.process_text_embeddings,
            activities.process_image_embeddings,
            activities.store_document_metadata,
            activities.store_text_embeddings,
            activities.store_image_embeddings
        ]
    )
    
    logger.info("Worker starting with task queue: document-task-queue")
    await worker.run()


# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
#     asyncio.run(start_worker())
