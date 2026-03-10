import os
from typing import List
import tempfile

from app.integrations.storage.azure_blob_storage import AzureStorageService
from app.knowledge_unit_factory.image_knowledge_unit import ImageKnowledgeUnit
from app.knowledge_unit_factory.text_knowledge_unit import TextKnowledgeUnit
from app.integrations.embeddings.local_openai import E5EmbeddingService, ImageEmbeddingService
from app.extractor.content import ExtractedContent
import uuid
import logging


logger = logging.getLogger(__name__)


class KnowledgeUnitsFactory:
    def __init__(
            self,
            text_embedder: E5EmbeddingService,
            image_embedder: ImageEmbeddingService,
            storage: AzureStorageService,
    ):
        # TODO: Get the text and image embedder from the app state
        self.text_embedder = text_embedder
        self.image_embedder = image_embedder
        self.blob_storage = storage


    def build_text_knowledge_units(self, content: ExtractedContent, file_id: uuid.UUID) -> List[TextKnowledgeUnit]:
        text_knowledge_units: List[TextKnowledgeUnit] = []
        total_pages = len(content.page_content)
        for i, content in enumerate(content.page_content):
            text = content.page_text

            text_embeddings = self.text_embedder.embed_query(text, "passage")
            text_k_unit = TextKnowledgeUnit.create(
                file_id=file_id,
                page_number=content.page_number,
                text=text,
                embedding=text_embeddings.tolist(),
            )
            logger.info(f'Successfully processed {i} out of {total_pages}')

            text_knowledge_units.append(text_k_unit)
        return text_knowledge_units

    def build_image_knowledge_units(self, user_book_images_dir: str, file_id: uuid.UUID):
        # Target prefix pattern = {user_id}/{file_id}/page_{page_num}_vis_{i}.jpg
        target_prefix = "/".join(user_book_images_dir.split('/')[-2:])
        image_knowledge_units: List[ImageKnowledgeUnit] = []
        blob_list = self.blob_storage.get_container_client("image").list_blobs(name_starts_with=target_prefix)
        for item in blob_list:
            if str(type(item)) == "<class 'azure.storage.blob._models.BlobPrefix'>":
                print(f"[DIRECTORY] {item.name}")
            else:
                blob_client = self.blob_storage.get_container_client("image").get_blob_client(
                    item.name
                )

                page_num = item.name.split('/')[-1].split('_')[1]
                with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                    data = blob_client.download_blob().readall()
                    temp_file.write(data)
                    temp_file.flush()

                    img_path = temp_file.name
                    embedding = self.image_embedder.embed_image(img_path)
                    img_knowledge_unit = ImageKnowledgeUnit.create(
                        file_id=file_id,
                        page_number=page_num,
                        image_path=item.name,
                        embedding=embedding,
                    )

                    image_knowledge_units.append(img_knowledge_unit)
                    print(f"[FILE] {item.name}")
        return image_knowledge_units


def build_text_knowledge_units(contents: ExtractedContent, file_id: uuid.UUID, text_embedder: E5EmbeddingService) -> List[TextKnowledgeUnit]:
    text_knowledge_units: List[TextKnowledgeUnit] = []
    total_pages = len(contents.page_content)
    for i, content in enumerate(contents.page_content):
        text = content.page_text

        text_embeddings = text_embedder.embed_query(text, "passage")
        text_k_unit = TextKnowledgeUnit.create(
            file_id=file_id,
            page_number=content.page_number,
            text=text,
            embedding=text_embeddings.tolist(),
        )
        logger.info(f'Successfully processed {i} out of {total_pages}')

        text_knowledge_units.append(text_k_unit)
    return text_knowledge_units

# FIXME: Pass the user file images from azure
def build_image_knowledge_units(user_book_images_dir: str, file_id: uuid.UUID, image_embedder: ImageEmbeddingService) -> List[ImageKnowledgeUnit]:
    image_knowledge_units: List[ImageKnowledgeUnit] = []
    images = os.listdir(user_book_images_dir)
    i = 0
    total_images = len(images)
    for img in images:
        name_split = img.split("_")
        page_number = int(name_split[1])

        img_path = os.path.join(user_book_images_dir, img)
        # TODO: Change this image path to azure image path
        img_embeddings = image_embedder.embed_image(img_path)

        image_knowledge_unit = ImageKnowledgeUnit.create(
            file_id=file_id,
            page_number=page_number,
            image_path=img,
            embedding=img_embeddings,
        )
        logger.info(f'Successfully processed {i} out of {total_images}')
        i+=1

        image_knowledge_units.append(image_knowledge_unit)
    return image_knowledge_units


def build_image_knowledge_units_azure(book_images_dir: str, file_id: uuid.UUID, storage: AzureStorageService, image_embedder: ImageEmbeddingService):
    # Target prefix pattern = {user_id}/{file_id}/page_{page_num}_vis_{i}.jpg
    target_prefix = "/".join(book_images_dir.split('/')[-2:])
    image_knowledge_units: List[ImageKnowledgeUnit] = []
    blob_list = storage.get_container_client("image").list_blobs(name_starts_with=target_prefix)
    for item in blob_list:
        if str(type(item)) == "<class 'azure.storage.blob._models.BlobPrefix'>":
            print(f"[DIRECTORY] {item.name}")
        else:
            blob_client = storage.get_container_client("image").get_blob_client(
                item.name
            )


            page_num = item.name.split('/')[-1].split('_')[1]
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                data = blob_client.download_blob().readall()
                temp_file.write(data)
                temp_file.flush()

                img_path = temp_file.name
                embedding = image_embedder.embed_image(img_path)
                img_knowledge_unit = ImageKnowledgeUnit.create(
                    file_id=file_id,
                    page_number=page_num,
                    image_path=item.name,
                    embedding=embedding,
                )

                image_knowledge_units.append(img_knowledge_unit)
                print(f"[FILE] {item.name}")
    return image_knowledge_units