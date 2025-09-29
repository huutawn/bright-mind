from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    user_id: Optional[int] = None


class AuthReq(BaseModel):
    email: EmailStr
    password: str
