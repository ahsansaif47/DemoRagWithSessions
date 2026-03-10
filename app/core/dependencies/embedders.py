from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService
from fastapi import Request


def init_text_embedder():
    return E5EmbeddingService()

def init_image_embedder():
    return ImageEmbeddingService()

def get_text_embedder(request: Request) -> E5EmbeddingService:
    return request.app.state.text_embedder

def get_image_embedder(request: Request) -> ImageEmbeddingService:
    return request.app.state.image_embedder
