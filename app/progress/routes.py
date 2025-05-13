from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .service import ProgressService
from ..auth.service import AuthService

# Crear un router específico para la gestión del progreso del usuario.
router = APIRouter(prefix="/progress", tags=["Progress"])
#modelo base para progress
class ProgressBase(BaseModel):
    level_id: int
    score: int    
#registro de progress 
class ProgressCreate(ProgressBase):
    pass
#progress que se devuelve en las respuestas
class Progress(ProgressBase):
    progress_id: int
    user_id: str
    start_date: datetime
    completion_date: Optional[datetime] = None
    
class Config:
        orm_mode = True

@router.get("/", response_model=List[Progress])
async def get_user_progress(authorization: Optional[str] = Header(None)):
    """
    Obtiene el progreso de un usuario autenticado.

    Args:
        authorization (str, optional): Token de autorización en formato Bearer.

    Raises:
        HTTPException: Si el token no está presente o no es válido.

    Returns:
        List[Progress]: Lista con el progreso de los niveles del usuario.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #extraer y verificar el token
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    # Obtener el progreso del usuario desde el servicio
    user_progress = await ProgressService.get_user_progress(decoded_token["uid"])
    return user_progress

@router.post("/", response_model=Progress, status_code=status.HTTP_201_CREATED)
async def record_progress(progress: ProgressCreate, authorization: Optional[str] = Header(None)):
    """
    Registra el progreso de un usuario en un nivel específico.

    Args:
        progress (ProgressCreate): Datos del progreso a registrar.
        authorization (str, optional): Token de autorización en formato Bearer.

    Raises:
        HTTPException: Si el token no está presente o no es válido.

    Returns:
        Progress: El registro del progreso creado.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    
    # Registrar el progreso utilizando el servicio correspondiente
    new_progress = await ProgressService.record_progress(
        user_id=decoded_token["uid"],
        level_id=progress.level_id,
        score=progress.score
    )
    return new_progress

