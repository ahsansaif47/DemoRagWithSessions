import uuid
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class TextKnowledgeUnit:
    id: uuid.UUID
    file_id: uuid.UUID
    text: str
    page_number: int
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = field(default=None)

    @staticmethod
    def create(
            file_id: uuid.UUID,
            page_number: int,
            text: str,
            embedding: Optional[List[float]] = None,
    ) -> "TextKnowledgeUnit":
        return TextKnowledgeUnit(
            id=uuid.uuid4(),
            file_id=file_id,
            page_number=page_number,
            text=text,
            embedding=embedding,
        )