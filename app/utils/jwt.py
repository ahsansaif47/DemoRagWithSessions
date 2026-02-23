
from datetime import datetime, timedelta
from jose import jwt
from dataclasses import dataclass, asdict

@dataclass
class Claim:
    user_id: str
    email: str

class JWTHandler:
    def __init__(self, secret_key: str, algorithm: str = "HS256", expiration: int = 3600):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration = expiration

    def create_jwt(self, claim: Claim):
        data = asdict(claim)
        expiry_time = datetime.utcnow() + timedelta(seconds=self.expiration)
        data.update({"exp": expiry_time})
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def verify_jwt(self, token: str):
        raise NotImplementedError()