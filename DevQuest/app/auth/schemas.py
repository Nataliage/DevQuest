from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    uid: str
    registration_date: datetime
    premium: bool = False
    role: str = "user"
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True