from fastapi import APIRouter, Depends, HTTPException, status, Header, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .service import AuthService
from .schemas import User, UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    uid: str
    email: str
    token: str
    role: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):    
    user_record = await AuthService.create_user(
        email=user.email,
        password=user.password,
        display_name=user.username
    )    
    return {
        "message": "Usuario registrado correctamente",
        "uid": user_record.uid,
        "email": user_record.email
    }

@router.post("/verify-token")
async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    
    return {
        "valid": True,
        "uid": decoded_token["uid"],
        "email": decoded_token.get("email", "")
    }