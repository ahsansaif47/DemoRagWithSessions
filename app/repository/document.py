import logging
import uuid
from datetime import datetime, timezone
from app.dto.document import DocData
from typing import List
from app.utils.utils import chunked, generate_batches
from app.models.document import DocumentModel, DocumentTextModel, DocumentImageModel

logger = logging.getLogger(__name__)


class DocumentRepository:
    def __init__(self, conn):
        self.conn = conn
        self.document_columns = ["id", "user_id", "file_name", "file_size", "created_at", "deleted_at"]
        self.document_texts = ["id", "file_id", "page_number", "content", "embedding", "created_at", "deleted_at"]
        self.document_images = ["id", "file_id", "page_number", "image_path", "embedding", "created_at", "deleted_at"]
        self.document_columns_str = ", ".join(self.document_columns)
        self.document_texts_str = ", ".join(self.document_texts)
        self.document_images_str = ", ".join(self.document_images)


    def add_document(self, doc: DocData) -> uuid.UUID | None:
        try:
            with self.conn.cursor() as cursor:
                placeholders = ",".join(["%s"] * len(self.document_columns))
                query = f'INSERT INTO files({self.document_columns_str}) VALUES({placeholders})'

                doc_model = DocumentModel(
                    file_id=doc.file_id,
                    user_id=doc.user_id,
                    file_name=doc.file_name,
                    file_size=doc.file_size
                )

                values = (
                    uuid.UUID(doc_model.file_id),
                    doc_model.user_id,
                    doc_model.file_name,
                    doc_model.file_size,
                    doc_model.created_at,
                    None
                )

                cursor.execute(query, values)
                self.conn.commit()

                logger.info(f"Repo: Document {doc_model.file_name} added to {doc_model.user_id}")
                return uuid.UUID(doc.file_id)
        except Exception as e:
            logger.error(f'Repo: Document Upload Error: {str(e)}')
            self.conn.rollback()
            raise e

    def batch_insert(self, query: str, data: list, batch_size=100):
        try:
            with self.conn.cursor() as cursor:
                for batch in generate_batches(data, batch_size):
                    cursor.executemany(
                        query, batch
                    )
                self.conn.commit()

        except Exception as e:
            logger.error(f'Batch Insert Error: {str(e)}')

    def add_document_text(self, doc_texts: List[DocumentTextModel]):
        try:
            document_texts_placeholders = ",".join(["%s"] * len(self.document_texts))
            text_embeddings_query = f'INSERT INTO document_texts({self.document_texts_str}) VALUES({document_texts_placeholders})'

            data = [
                (
                    uuid.uuid4(),
                    str(doc_text.file_id),
                    doc_text.page_number,
                    doc_text.content,
                    doc_text.embedding,
                    datetime.now(timezone.utc),
                    None
                )
                for doc_text in doc_texts
            ]

            self.batch_insert(text_embeddings_query, data)
        except Exception as e:
            logger.error(f'Repo: Document Text Upload Error: {str(e)}')
            self.conn.rollback()
            raise e

    def add_document_images(self, doc_images: List[DocumentImageModel]):
        try:
            document_images_placeholders = ",".join(["%s"] * len(self.document_images))
            image_embeddings_query = f'INSERT INTO document_images({self.document_images_str}) VALUES({document_images_placeholders})'

            data = [
                (
                    uuid.uuid4(),
                    str(doc_img.file_id),
                    doc_img.page_number,
                    doc_img.image_path,
                    doc_img.embedding,
                    datetime.now(timezone.utc),
                    None
                )
                for doc_img in doc_images
            ]

            self.batch_insert(image_embeddings_query, data)
        except Exception as e:
            logger.error(f'Repo: Document Images Upload Error: {str(e)}')
            self.conn.rollback()
            raise e

    def remove_document(self, doc_id: str) -> bool:
        try:
            with self.conn.cursor() as cursor:
                # Mark Document Text Soft Deleted
                soft_delete_file_text_q = "UPDATE document_texts SET deleted_at = '%s' WHERE file_id = '%s'"
                values = (datetime.now(timezone.utc), doc_id)
                cursor.execute(soft_delete_file_text_q, values)

                # Mark Document Images Soft Deleted
                soft_delete_file_images_q = "UPDATE document_images SET deleted_at = '%s' WHERE file_id = '%s'"
                cursor.execute(soft_delete_file_images_q, values)

                # Soft Delete File Record Itself
                query = "UPDATE files SET deleted_at = '%s' WHERE file_id = '%s'"
                cursor.execute(query, values)

                self.conn.commit()

                logger.info(f"Repo: Document {doc_id} Images Removed")
                logger.info(f"Repo: Document {doc_id} Text Removed")
                logger.info(f"Repo: Document {doc_id} Removed")

                return True
        except Exception as e:
            logger.error(f'Repo: Document Removal Error: {str(e)}')
            self.conn.rollback()
            raise e
