from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class UserOut(UserBase):
    id: int
    city: Optional[str] = None
    profile_photo: Optional[str] = None
    cover_photo: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    device_id: Optional[str] = None
    is_deleted: int

    class Config:
        from_attributes = True
