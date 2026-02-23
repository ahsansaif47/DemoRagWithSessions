from app.service.auth import JWTAuthService
from app.dto.users import (
    UserRegistrationRequestDTO,
    UserLoginRequestDTO,
    UserRegistrationResponseDTO,
    UserLoginResponseDTO,
)
import logging

logger = logging.getLogger(__name__)


class JWTAuthHandler:

    def __init__(self, auth_service: JWTAuthService):
        self.auth_service = auth_service

    def signup(self, data: UserRegistrationRequestDTO) -> UserRegistrationResponseDTO | None:
        return self.auth_service.signup(data)

    def login(self, data: UserLoginRequestDTO):
        return self.auth_service.login(data)
