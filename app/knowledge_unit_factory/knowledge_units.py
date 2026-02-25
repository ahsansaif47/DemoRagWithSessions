from app.knowledge_unit_factory.text_knowledge_unit import TextKnowledgeUnit
from app.integrations.embeddings.local_openai import E5EmbeddingService
from app.extractor.content import ExtractedContent
import uuid


def build_knowledge_units(contents: ExtractedContent, file_id: uuid.UUID):
    text_embedder = E5EmbeddingService()

    text_knowledge_units = []
    image_knowledge_units = []
    for idx, content in enumerate(contents.page_content):
        text = content.page_text

        text_embeddings = text_embedder.embed_query(text, "passage")
        text_k_unit = TextKnowledgeUnit.create(
            file_id=file_id,
            page_number=content.page_number,
            text=text,
            embedding=text_embeddings,
        )

        text_knowledge_units.append(text_k_unit)

