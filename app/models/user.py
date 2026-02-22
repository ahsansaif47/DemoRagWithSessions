from pydantic import BaseModel


class UserModel(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    phone: str