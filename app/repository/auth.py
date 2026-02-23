import uuid
from app.dto.users import UserLoginRequestDTO, UserRegistrationRequestDTO
from datetime import datetime
from psycopg import errors
from app.domain import exceptions
from app.models.user import UserModel


class JWTAuthRepository:
    # FIXME: I need the logger in the init function for logging
    def __init__(self, conn):
        self.conn = conn
        self.user_columns = ["id", "username", "email", "phone_no", "password_hash", "created_at","updated_at", "deleted_at"]
        self.cols_str = ", ".join(self.user_columns)

    def signup(self, user: UserRegistrationRequestDTO) -> uuid.UUID | None:
        try:
            with self.conn.cursor() as cursor:
                placeholders = ",".join(["%s"] * len(self.user_columns))
                query = f"INSERT INTO users({self.cols_str}) VALUES({placeholders})"

                trans_id = uuid.uuid4()
                # TODO: Generate the password hash here and use it in the repo layer onwards
                password_hash = ""
                now = datetime.now()
                values = (
                    trans_id,
                    user.name,
                    user.email,
                    user.phone_number,
                    password_hash,
                    now.utcnow(),
                    now.utcnow(),
                    None
                )
                cursor.execute(query, values)
                self.conn.commit()
                return trans_id
        except errors.UniqueViolation:
            self.conn.rollback()
            raise exceptions.UserAlreadyExists()
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_user_by_email(self, email: str) -> UserModel | None:
        try:
            with self.conn.cursor() as cursor:
                query = f"SELECT {self.cols_str} FROM users WHERE email = '{email}'"
                cursor.execute(query)
                matched_user = cursor.fetchone()

                if not matched_user:
                    return None

                return UserModel(
                    user_id=matched_user[0],
                    username=matched_user[1],
                    email=matched_user[2],
                    phone=matched_user[3],
                    password_hash=matched_user[4],
                    created_at=matched_user[5],
                    updated_at=matched_user[6],
                    deleted_at=matched_user[7]
                )
        except Exception as e:
            # TODO: Log using the logger from the class
            return None
