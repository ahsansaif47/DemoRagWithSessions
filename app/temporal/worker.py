import asyncio
from temporalio.client import Client

from app.core.dependencies.azure_storage import get_azure_storage_service
from app.repository.document import DocumentRepository
from app.repository.database import get_database_connection
from temporalio.worker import Worker

from app.temporal.activities.document_activities import DocumentActivities


async def start_worker():

    client = await Client.connect("localhost:7233")

    repo = DocumentRepository(get_database_connection)
    storage = get_azure_storage_service()

    activities = DocumentActivities(
        storage=repo,
        repo=repo,
        extractor=repo,
        ku_factory=repo,
    )

    # TODO: Get the activities initialized over here

    worker = Worker(
        client=client,
        task_queue="document-task-queue",
        workflows=[],
        activities=[]
    )

    await worker.run()
