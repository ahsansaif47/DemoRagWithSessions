from app.dto.users import (
    UserRegistrationRequestDTO,
    UserLoginRequestDTO,
    UserRegistrationResponseDTO,
    UserCreatedData, UserLoginResponseDTO
)
from app.utils import utils, jwt
from app.repository.auth import JWTAuthRepository
import logging

logger = logging.getLogger(__name__)


class JWTAuthService:
    def __init__(self, user_repository: JWTAuthRepository):
        self.user_repository = user_repository

    def signup(self, data: UserRegistrationRequestDTO) -> UserRegistrationResponseDTO | None:
        try:
            user_id = self.user_repository.signup(data)
            if user_id is not None:
                user_data = UserCreatedData()
                # TODO: Might need to convert user_id to string..
                # Currently its uuid.UUID
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
            logger.error(f'Service: Failed to Create User: {str(e)}')
            return None

    def login(self, data: UserLoginRequestDTO) -> UserLoginResponseDTO | None:
        try:
            jwt_handler = jwt.JWTHandler("")
            user_data = self.user_repository.get_user_by_email(data.email)
            if user_data is not None:

                if user_data.deleted_at is not None:
                    pass

                response = UserLoginResponseDTO()
                password_status = utils.verify_password(data.password, user_data.password_hash)
                if not password_status:
                    logger.info("Service: Invalid User Credentials")
                    response.status = "401"
                    response.message = "Invalid Credentials"
                    return response


                jwt_claim = jwt.Claim(
                    user_id=user_data.user_id,
                    email=user_data.email
                )
                # TODO: Generate the JWT Token using the jwt in utils
                jwt_token = jwt_handler.create_jwt(jwt_claim)

                response.status = "200"
                response.message = "Login Successful"
                response.jwt_token = jwt_token
                response.user_id = user_data.user_id
                return response

            return None
        except Exception as e:
            logger.error(f'Service: Failed to Login User: {str(e)}')
            pass
