
from datetime import datetime, timedelta
from jose import jwt
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

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

    def decode_token(self, token:str) -> Claim | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=self.algorithm)
            claim = Claim(
                payload["user_id"],
                payload["email"],
            )
            return claim
        except Exception as e:
            logger.error(f'JWT Decoding Error: {str(e)}')
            return None
