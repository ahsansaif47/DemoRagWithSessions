from fastapi import Depends
from app.repository.auth import JWTAuthRepository
from app.service.auth import JWTAuthService
from app.api.handlers.auth import JWTAuthHandler
from app.core.dependencies.database import get_database

def get_auth_repository(db=Depends(get_database)):
    return JWTAuthRepository(db)

def get_auth_service(repo=Depends(get_auth_repository)):
    return JWTAuthService(repo)

def get_auth_handlers(service=Depends(get_auth_service)):
    return JWTAuthHandler(service)