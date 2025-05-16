from fastapi import APIRouter, Depends, HTTPException, status, Header, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from firebase_admin import auth
from app.config.firebase import db, FIREBASE_API_KEY
import requests
from .service import AuthService
from .schemas import User, UserCreate, UserLogin, UserRegister, LoginResponse
from app.progress.service import ProgressService

router = APIRouter(prefix="/auth", tags=["Authentication"])

    
@router.post("/login", response_model=LoginResponse)
async def login(user: UserLogin):      
    #autenticar con firebase REST API
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    response = requests.post(url, json={
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    })
                   
    if response.status_code != 200:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",                    
            )
    login_info = response.json()
    token = login_info.get("idToken")
    uid = login_info.get("localId")
    if not token or not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al obtener el token de autenticación",
        )
    #obtener datos del user desde Firebase
    user_doc = db.collection("users").document(uid).get()
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado en la base de datos",
        )
        
    user_data = user_doc.to_dict()
    
    #obtener el progress desde firebase
    levels_completed = await ProgressService.get_levels_completed_by_user(uid) 
            
    #actualizamos last login
    db.collection("users").document(uid).update({
        "last_login": datetime.utcnow()
    })
    #response del backend
    return {
        "auth": token,        
        "email": user_data.get("email"),
        "username": user_data.get("username"),
        "role": user_data.get("role", "user"),        
        "levels_completed": levels_completed
        #"uid": uid,
    }    
        
            
          
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=LoginResponse)
async def register(user: UserRegister):    
    user_record = await AuthService.create_user(
        email=user.email,
        password=user.password,
        display_name=user.username
    )    
    token = auth.create_custom_token(user_record.uid).decode("utf-8")    
    levels_completed = await ProgressService.get_levels_completed_by_user(user_record.uid)
    return {
        #"message": "Usuario registrado correctamente",
        "auth": token,
        "username": user.username,        
        "email": user_record.email,
        "role": "user",
        "levels_completed": levels_completed
        #"uid": user_record.uid,
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