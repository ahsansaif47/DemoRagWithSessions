from app.dto.users import UserRegistrationRequestDTO, UserLoginRequestDTO


class JWTAuthService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def signup(self, data: UserRegistrationRequestDTO):
        raise NotImplementedError()

    def login(self, data: UserLoginRequestDTO):
        raise NotImplementedError()