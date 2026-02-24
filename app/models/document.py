from datetime import datetime


class DocumentModel:
    def __init__(self, file_id, user_id, file_name, file_size):
        self.file_id = file_id
        self.user_id = user_id
        self.file_name = file_name
        self.file_size = file_size
        self.created_at = datetime.now().utcnow()
        self.updated_at = datetime.now().utcnow()
