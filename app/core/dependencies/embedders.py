from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService
from functools import lru_cache

@lru_cache
def get_text_embedder() -> E5EmbeddingService:
    return E5EmbeddingService()

@lru_cache
def get_image_embedder() -> ImageEmbeddingService:
    return ImageEmbeddingService()
