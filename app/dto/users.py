from pydantic import validator, EmailStr, Field, BaseModel, field_validator
from datetime import datetime
from app.utils import validation


# TODO: FIX the redundant functions in DTO classes
class UserRegistrationRequestDTO(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("password")
    @staticmethod
    def password_must_be_strong(cls, v):
        valid, msg = validation.check_strong_password(v)
        if not valid:
            raise ValueError(msg)
        UserRegistrationRequestDTO.password = v

    @field_validator("phone_number")
    @staticmethod
    def phone_must_be_valid(cls, v):
        valid, msg = validation.validate_phone(v)
        if not valid:
            raise ValueError(msg)
        UserRegistrationRequestDTO.phone_number = v

    @field_validator("name")
    @staticmethod
    def name_must_be_valid(cls, v):
        valid, msg = validation.validate_name(v)
        if not valid:
            raise ValueError(msg)
        return v


class UserCreatedData(BaseModel):
    user_id: str
    email: EmailStr
    is_verified: bool


class UserRegistrationResponseDTO(BaseModel):
    status: str
    message: str
    data: UserCreatedData


class UserLoginRequestDTO(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponseDTO(BaseModel):
    status: str
    message: str
    jwt_token: str
    user_id: str


class UpdateUserRequestDTO:
    phone_no: str
    password: str

    @field_validator("password")
    @staticmethod
    def password_must_be_strong(cls, v):
        valid, msg = validation.check_strong_password(v)
        if not valid:
            raise ValueError(msg)
        UpdateUserRequestDTO.password = v

    @field_validator("phone_number")
    @staticmethod
    def phone_must_be_valid(cls, v):
        valid, msg = validation.validate_phone(v)
        if not valid:
            raise ValueError(msg)
        UpdateUserRequestDTO.phone_no = v
