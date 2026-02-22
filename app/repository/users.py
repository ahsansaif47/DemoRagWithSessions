# FIXME: Change the import to get it from somewhere else not making a cyclic import
from database import PostgresPool
import uuid
from app.dto.users import UserRegistrationRequestDTO, UpdateUserRequestDTO
from datetime import datetime


class UsersRepository:
    # FIXME: Pass the logger to repository layer
    def __init__(self, conn):
        self.connection = conn
        self.user_columns = ["id", "username", "email", "phone_no", "password_hash", "created_at","updated_at", "deleted_at"]
        self.cols_str = ", ".join(self.user_columns)

    def get_users(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT {self.cols_str} FROM users WHERE deleted_at is NULL")
            return cursor.fetchall()
        except Exception as e:
            # TODO: Log this exception using the injected logger
            return None

    def get_user_by_id(self, user_id: int):
        try:
            cursor = self.connection.cursor()
            cols_str = ",".join(self.user_columns)
            cursor.execute(f"SELECT {cols_str} FROM users WHERE id = {user_id} AND deleted_at is NULL")
            return cursor.fetchone()
        except Exception as e:
            # TODO: Log this exception using the injected logger
            return None

    def delete_user(self, user_id: int):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE users SET deleted_at = {datetime.now().utcnow()} WHERE user_id = {user_id}")
            self.connection.commit()
        except Exception as e:
            # TODO: Log this exception using the injected logger
            return None

    def update_user(self, user: UpdateUserRequestDTO):
        raise NotImplemented()

    def get_books_by_user_id(self, user_id: int):
        try:
            cursor = self.connection.cursor()
        except Exception as e:
            # TODO: Log this exception using the injected logger
            return e