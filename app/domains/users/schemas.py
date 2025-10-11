from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: str
    phone: Optional[str] =None
    logo: Optional[str] = None
    model_config=ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    role: str
    user_profile: Optional['UserProfileResponse'] = None
    last_login: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class UserCreateReq(UserBase):
    email: EmailStr
    password: str
    role: str = 'user'


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    type: Optional[str] = None
    jti: Optional[str] = None


class UpdateUserReq(UserBase):
    logo: Optional[str] = None
    is_active: Optional[bool] = True

class DonorResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: Optional[str]
    phone: Optional[str] = None
    is_anonymous: bool
    model_config=ConfigDict(from_attributes=True)

    