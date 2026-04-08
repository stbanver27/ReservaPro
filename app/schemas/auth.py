from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
