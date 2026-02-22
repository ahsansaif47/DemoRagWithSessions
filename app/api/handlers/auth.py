from app.dto.users import UserRegistrationRequestDTO, UserLoginRequestDTO

class JWTAuthHandler:

    def __init__(self, user_service, token_service):
        self.user_service = user_service
        self.token_service = token_service

    def signup(self, data: UserRegistrationRequestDTO):
        raise NotImplementedError()

    def login(self, data: UserLoginRequestDTO):
        raise NotImplementedError()