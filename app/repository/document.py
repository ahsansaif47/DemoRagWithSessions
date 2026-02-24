import logging
import uuid
from datetime import datetime
from app.dto.document import DocData

from app.models.document import DocumentModel

logger = logging.getLogger(__name__)


class DocumentRepository:
    def __init__(self, conn):
        self.conn = conn
        self.document_columns = ["id", "user_id", "file_name", "file_size", "created_at", "updated_at"]
        self.document_columns_str = ", ".join(self.files_columns)

    def add_document(self, doc: DocData) -> uuid.UUID | None:
        try:
            with self.conn.cursor() as cursor:
                placeholders = ",".join(["%s"] * len(self.document_columns))
                query = f'INSERT INTO files({self.document_columns_str}) VALUES({placeholders})'
                trans_id = uuid.uuid4()

                doc_model = DocumentModel(
                    file_id=trans_id,
                    user_id=doc.user_id,
                    file_name=doc.file_name,
                    file_size=doc.file_size
                )

                values = (
                    doc_model.file_id,
                    doc_model.user_id,
                    doc_model.file_name,
                    doc_model.file_size,
                    doc_model.created_at,
                    doc_model.updated_at
                )

                cursor.execute(query, values)
                self.conn.commit()

                logger.info(f"Repo: Document {doc_model.file_name} added to {doc_model.user_id}")
                return trans_id
        except Exception as e:
            logger.error(f'Repo: Document Upload Error: {str(e)}')
            self.conn.rollback()
            raise e

    def remove_document(self, doc_id: str) -> bool:
        try:
            with self.conn.cursor() as cursor:
                # Mark Document Text Soft Deleted
                soft_delete_file_text_q = "UPDATE document_texts SET deleted_at = '%s' WHERE file_id = '%s'"
                values = (datetime.now().utcnow(), doc_id)
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
