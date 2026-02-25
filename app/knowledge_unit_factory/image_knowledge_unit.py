from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import uuid


@dataclass
class ImageKnowledgeUnit:
    id: uuid.UUID
    file_id: uuid.UUID
    page_number: int
    image_path: str
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = field(default=None)

    @staticmethod
    def create(
            file_id: uuid.UUID,
            page_number: int,
            image_path: str,
            embedding: Optional[List[float]],
    )-> "ImageKnowledgeUnit":
        return ImageKnowledgeUnit(
            id=uuid.uuid4(),
            file_id=file_id,
            page_number=page_number,
            image_path=image_path,
            embedding=embedding,
        )