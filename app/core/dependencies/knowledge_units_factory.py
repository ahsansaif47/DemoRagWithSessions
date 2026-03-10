from fastapi import Request
from app.knowledge_unit_factory.knowledge_units import KnowledgeUnitsFactory
from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService
from app.integrations.storage.azure_blob_storage import AzureStorageService


def init_knowledge_unit_factory(
        text_embedder: E5EmbeddingService,
        image_embedder: ImageEmbeddingService,
        storage: AzureStorageService,
):
    return KnowledgeUnitsFactory(
        text_embedder=text_embedder,
        image_embedder=image_embedder,
        storage=storage
    )

def get_knowledge_units_factory(request: Request) -> KnowledgeUnitsFactory:
    return request.app.state.knowledge_units_factory