from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserRegister(BaseModel):
    """Datos requeridos para registrar un nuevo usuario"""
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    """Datos requeridos para iniciar sesión"""
    email: EmailStr
    password: str
class UserRegisterResponse(BaseModel):
    """Respuesta devuelta al frontend al registrar un nuevo usuario"""
    auth: str    
    email: EmailStr
    username: str
    role: str    
    levels_completed: Optional[List[int]] = None
    #uid: str
class LoginResponse(BaseModel):
    """Respuesta devuelta al frontend al iniciar sesión"""
    auth: str    
    email: EmailStr
    username: str    
    role: str    
    levels_completed: Optional[List[int]] = None
    #progress: Optional[List[Dict[str, Any]]] = None
    #uid: str
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