import uuid
from app.dto.users import UserLoginRequestDTO, UserRegistrationRequestDTO
from datetime import datetime


class JWTAuthRepository:
    # FIXME: I need the logger in the init function for logging
    def __init__(self, conn):
        self.conn = conn
        self.user_columns = ["id", "username", "email", "phone_no", "password_hash", "created_at","updated_at", "deleted_at"]
        self.cols_str = ", ".join(self.user_columns)

    def signup(self, user: UserRegistrationRequestDTO):
        try:
            with self.conn.cursor() as cursor:
                placeholders = ",".join(["%s"] * len(self.user_columns))
                query = f"INSERT INTO({self.cols_str}) VALUES({placeholders})"

                trans_id = uuid.uuid4()
                # Replace the password hash with this empty password hash
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
        except Exception as e:
            return e

    def login(self, user: UserLoginRequestDTO):
        try:
            with self.conn.cursor() as cursor:
                # TODO: Generate the password hash here and use it in the repo layer onwards
                password_hash = ""
                query = f"SELECT {self.cols_str} FROM users WHERE email = '{user.email}'"
                cursor.execute(query)
                matched_user = cursor.fetchone()
                if matched_user is not None:
                    matched_user = matched_user[0]

                    # Get the deleted at value from the very last
                    user_archived = matched_user[-1]
                    if user_archived is not None:
                        return "user_archived"

                    db_password_hash = matched_user[4]
                    if db_password_hash == password_hash:
                        # TODO: Generate the token here and return it back
                        pass
        except Exception as e:
            # TODO: Log using the logger from the class
            raise e
