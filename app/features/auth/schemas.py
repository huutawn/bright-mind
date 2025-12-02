from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
class Token(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime

class TokenPayload(BaseModel):
    user_id: Optional[int] = None


class AuthReq(BaseModel):
    email: EmailStr
    password: str
