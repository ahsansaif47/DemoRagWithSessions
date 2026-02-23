from pydantic import BaseModel
from datetime import datetime

from app.dto.users import UserLoginRequestDTO


class UserModel:
    def __init__(self, user_id, username, email, phone, password_hash, created_at, updated_at, deleted_at):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
