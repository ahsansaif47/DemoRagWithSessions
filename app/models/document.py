from datetime import datetime, timezone


class DocumentModel:
    def __init__(self, file_id, user_id, file_name, file_size):
        self.file_id = file_id
        self.user_id = user_id
        self.file_name = file_name
        self.file_size = file_size
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class DocumentTextModel:
    def __init__(self, file_id, page_number, content, embedding):
        self.file_id = file_id
        self.page_number = page_number
        self.content = content
        self.embedding = embedding


class DocumentImageModel:
    def __init__(self, file_id, page_number, image_path, embedding):
        self.file_id = file_id
        self.page_number = page_number
        self.image_path = image_path
        self.embedding = embedding
