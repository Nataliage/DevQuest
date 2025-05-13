from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    """Datos requeridos para iniciar sesión"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """Respuesta devuelta al frontend al iniciar sesión"""
    auth: str
    uid: str
    email: str
    username: str    
    role: str
    progress: Optional[List[Dict[str, Any]]] = None
    levels_completed: Optional[List[int]] = None
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