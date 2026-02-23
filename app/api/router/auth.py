from fastapi import APIRouter, Depends, HTTPException
from app.api.handlers.auth import JWTAuthHandler
from app.dto.users import (
    UserLoginRequestDTO,
    UserRegistrationRequestDTO,
    UserLoginResponseDTO,
    UserRegistrationResponseDTO
)
from app.core.dependencies.auth import get_auth_handlers


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserRegistrationResponseDTO)
def signup(
    data: UserRegistrationRequestDTO,
    handler: JWTAuthHandler = Depends(get_auth_handlers),
):
    try:
        return handler.signup(data)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=UserLoginResponseDTO)
def login(
    data: UserLoginRequestDTO,
    handler: JWTAuthHandler = Depends(get_auth_handlers),
):
    try:
        return handler.login(data)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
