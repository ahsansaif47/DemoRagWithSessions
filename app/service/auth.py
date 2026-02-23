from app.dto.users import (
    UserRegistrationRequestDTO,
    UserLoginRequestDTO,
    UserRegistrationResponseDTO,
    UserCreatedData, UserLoginResponseDTO
)
from app.utils import jwt
from app.repository.auth import JWTAuthRepository

class JWTAuthService:
    def __init__(self, user_repository: JWTAuthRepository):
        self.user_repository = user_repository

    def signup(self, data: UserRegistrationRequestDTO) -> UserRegistrationResponseDTO | None:
        try:
            user_id = self.user_repository.signup(data)
            if user_id is not None:
                user_data = UserCreatedData()
                # TODO: Might need to convert user_id to string..
                # TODO: Currently its uuid.UUID
                user_data.id = user_id
                user_data.email = data.email
                user_data.is_verified = False

                response = UserRegistrationResponseDTO()
                response.data = user_data
                response.status = "201"
                response.message = "User created successfully"

                return response
            return None
        except Exception as e:
            # TODO: Use the injected logger to log exception in here
            return None

    def login(self, data: UserLoginRequestDTO) -> UserLoginResponseDTO | None:
        try:
            user_data = self.user_repository.get_user_by_email(data.email)
            if user_data is not None:

                if user_data.deleted_at is not None:
                    pass

                if not jwt.verify_password(data.password, user_data.password_hash):
                    return None

                response = UserLoginResponseDTO()



        except Exception as e:
            pass