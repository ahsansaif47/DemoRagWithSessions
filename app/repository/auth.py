from app.dto.users import UserRegistrationRequestDTO
from datetime import datetime, timezone
from app.models.user import UserModel
from app.domain import exceptions
from psycopg import errors
from app.utils.utils import generate_password_hash
import logging
import uuid

logger = logging.getLogger(__name__)

class JWTAuthRepository:
    def __init__(self, conn):
        self.conn = conn
        self.user_columns = ["id", "name", "email", "phone_number", "password_hash", "created_at","updated_at", "deleted_at"]
        self.cols_str = ", ".join(self.user_columns)

    def signup(self, user: UserRegistrationRequestDTO) -> uuid.UUID | None:
        try:
            with self.conn.cursor() as cursor:
                placeholders = ",".join(["%s"] * len(self.user_columns))
                query = f"INSERT INTO users({self.cols_str}) VALUES({placeholders})"

                trans_id = uuid.uuid4()
                # TODO: Move this password hash part to service layer
                password_hash = generate_password_hash(user.password)
                now = datetime.now(timezone.utc)
                values = (
                    trans_id,
                    user.name,
                    user.email,
                    user.phone_number,
                    password_hash,
                    now,
                    now,
                    None
                )
                cursor.execute(query, values)
                self.conn.commit()

                logger.info(f"Repo: User Created with ID: {trans_id}")
                return trans_id
        except errors.UniqueViolation:
            logger.error(f"Repo: User Already Exists with ID: {trans_id}")
            self.conn.rollback()
            raise exceptions.UserAlreadyExists()
        except Exception as e:
            logger.error(f"Repo: General Signup Exception: {str(e)}")
            self.conn.rollback()
            raise e

    def get_user_by_email(self, email: str) -> UserModel | None:
        try:
            with self.conn.cursor() as cursor:
                query = f"SELECT {self.cols_str} FROM users WHERE email = '{email}'"
                cursor.execute(query)
                matched_user = cursor.fetchone()

                if not matched_user:
                    logger.info('Repo: No such email')
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
            logger.error(f'Repo: Login Exception: {str(e)}')
            return None
