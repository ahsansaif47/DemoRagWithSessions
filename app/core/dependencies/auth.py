from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from app.repository.auth import JWTAuthRepository
from app.service.auth import JWTAuthService
from app.api.handlers.auth import JWTAuthHandler
from app.repository.database import get_database_connection
from app.core.dependencies import config
from app.utils.jwt import JWTHandler
from app.utils.jwt import Claim
import logging

jwt_config = config.AppConfig().jwt_config

logger = logging.getLogger(__name__)

def get_auth_repository(db=Depends(get_database_connection)):
    return JWTAuthRepository(db)

def get_auth_service(repo=Depends(get_auth_repository)):
    return JWTAuthService(repo)

def get_auth_handlers(service=Depends(get_auth_service)):
    return JWTAuthHandler(service)


# TODO: Use this in the api handler to get jwt claims
security = HTTPBearer()
def get_jwt_claim(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Claim | None:
    try:
        jwt_handler = JWTHandler(jwt_config.secret_key)
        token = credentials.credentials
        return jwt_handler.decode_token(token)
    except Exception as e:
        logger.error(f'JWT Claim Decode Error: {str(e)}')
        raise HTTPException(status_code=401, detail="Invalid Token")