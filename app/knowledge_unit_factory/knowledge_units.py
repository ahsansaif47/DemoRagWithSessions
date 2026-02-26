import os
from typing import List

from app.knowledge_unit_factory.image_knowledge_unit import ImageKnowledgeUnit
from app.knowledge_unit_factory.text_knowledge_unit import TextKnowledgeUnit
from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService
from app.extractor.content import ExtractedContent
import uuid


def build_text_knowledge_units(contents: ExtractedContent, file_id: uuid.UUID) -> List[TextKnowledgeUnit]:
    text_embedder = E5EmbeddingService()

    text_knowledge_units: List[TextKnowledgeUnit] = []
    for _, content in enumerate(contents.page_content):
        text = content.page_text

        text_embeddings = text_embedder.embed_query(text, "passage")
        text_k_unit = TextKnowledgeUnit.create(
            file_id=file_id,
            page_number=content.page_number,
            text=text,
            embedding=text_embeddings,
        )

        text_knowledge_units.append(text_k_unit)
    return text_knowledge_units

def build_image_knowledge_units(user_book_images_dir: str, file_id: uuid.UUID) -> List[ImageKnowledgeUnit]:
    image_embedder = ImageEmbeddingService()

    image_knowledge_units: List[ImageKnowledgeUnit] = []
    images = os.listdir(user_book_images_dir)
    for img in images:
        name_split = img.split("_")
        page_number = int(name_split[1])
        img_embeddings = image_embedder.embed_image(img)

        image_knowledge_unit = ImageKnowledgeUnit.create(
            file_id=file_id,
            page_number=page_number,
            image_path=img,
            embedding=img_embeddings,
        )

        image_knowledge_units.append(image_knowledge_unit)
    return image_knowledge_units
