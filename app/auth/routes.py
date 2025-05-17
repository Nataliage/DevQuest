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
    
@router.post("/login", response_model=LoginResponse, summary="Iniciar sesión de usuario")
async def login(user: UserLogin):  
    """
    Endpoint para iniciar sesión de usuario.
    Args:
        user (UserLogin): Datos de login que incluyen email y contraseña.
    Raises:
        HTTPException 401: Credenciales inválidas o error al obtener token.
        HTTPException 404: Usuario no encontrado en base de datos.
    Returns:        
        dict: Contiene token de autenticación, email, username, role y niveles completados.
    """    
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
        
            
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=LoginResponse,
    summary="Registrar nuevo usuario y loguear automáticamente"
)
async def register(user: UserRegister):
    try:
        # Crear usuario con Firebase Admin
        user_record = await AuthService.create_user(
            email=user.email,
            password=user.password,
            display_name=user.username
        )
        custom_token = auth.create_custom_token(user_record.uid).decode("utf-8")

        # Autenticar usuario para obtener token oficial Firebase
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        response = requests.post(url, json={
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        })
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al iniciar sesión después del registro"
            )
        login_info = response.json()
        token = login_info.get("idToken")

        # Obtener progreso inicial (niveles completados)
        levels_completed = await ProgressService.get_levels_completed_by_user(user_record.uid) or []

        # Devolver token oficial y datos de usuario
        return {
            "auth": token,
            "username": user.username,
            "email": user_record.email,
            "role": "user",
            "levels_completed": levels_completed
        }

    except HTTPException:
        raise

    except Exception as e:
        msg = str(e).lower()
        if "email already exists" in msg or "email-already-exists" in msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya existe"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado en /register: {e}"
        )
    

@router.post("/verify-token", summary="Verificar token JWT")
async def verify_token(authorization: Optional[str] = Header(None)):
    """
    Verifica la validez de un token JWT.
    Args:
        authorization (str): Token JWT en header Authorization (Bearer).
    Raises:
        HTTPException 401: Token no proporcionado o formato incorrecto.
    Returns:
        dict: Estado de validez, uid y email asociado.
    """
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