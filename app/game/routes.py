from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional, List, Dict
from pydantic import BaseModel
from ..auth.service import AuthService
from .service import GameService

router = APIRouter(prefix="/game", tags=["Game"])

class CodeValidationRequest(BaseModel):
    """Modelo para solicitud de validación de código"""
    level_id: int
    code: str
    script: dict #agrego el campo del script

class CodeValidationResponse(BaseModel):
    """Modelo para respuesta de validación de código"""
    correct: bool
    score: int
    message: Optional[str] = None
    script: Optional[dict] = None
    
class LevelStateRequest(BaseModel):
    """Modelo para guardar el estado de un nivel"""
    level_id: int
    state: dict
    
# Nuevo modelo para validación de nivel de pociones
class PotionLevelRequest(BaseModel):
    """Modelo para validación de nivel de pociones"""
    level_id: int
    potions: Dict[str, int]  # {"VENENO": 3, "SALUD": 2}
    bloques_utilizados: List[str]  # ["if", "then", "else"]

class PotionLevelResponse(BaseModel):
    """Modelo para respuesta de validación de nivel de pociones"""
    correct: bool
    stars: int
    message: str
    pociones_correctas: int
    total_pociones: int
    bloques_utilizados: int
    bloques_optimales: int

@router.post("/validate-code", response_model=CodeValidationResponse)
async def validate_code_endpoint(request: CodeValidationRequest, authorization: Optional[str] = Header(None)):
    """
    Valida el código proporcionado por el usuario para resolver un nivel.
    
    - Requiere autenticación mediante token Bearer
    - Verifica si el código resuelve el problema del nivel
    - Retorna el resultado con puntuación y mensaje
    """    
    # validacion del token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)

    # Llamada al servicio para validar el código
    return await GameService.validate_code(decoded_token["uid"], request.level_id, request.code, request.script) 

@router.post("/save-level-state")
async def save_level_state(request: LevelStateRequest, authorization: Optional[str] = Header(None)):
    """
    Guarda el estado actual del nivel para el usuario.
    Útil para permitir continuar una partida más tarde.
    
    - Requiere autenticación mediante token Bearer
    - Guarda el estado del nivel en la base de datos
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)

    await GameService.save_level_state(decoded_token["uid"], request.level_id, request.state)
    return {"detail": "Estado guardado correctamente"}

@router.post("/exit")
async def exit_game(authorization: Optional[str] = Header(None)):
    """
    Registra que el usuario ha salido del juego.
    
    - Requiere autenticación mediante token Bearer
    - Útil para análisis de comportamiento y estadísticas
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)

    await GameService.exit_game(decoded_token["uid"])
    return {"detail": "Juego finalizado correctamente"}

@router.post("/validate-potion-level", response_model=PotionLevelResponse)
async def validate_potion_level(
    request: PotionLevelRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Valida si el usuario ha completado correctamente un nivel de pociones.
    
    - Requiere autenticación mediante token Bearer
    - Verifica si las cantidades de pociones coinciden con lo esperado
    - Evalúa si el número de bloques utilizados es óptimo
    - Asigna 0-3 estrellas según el rendimiento
        
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    
    return await GameService.validate_potion_level(
        decoded_token["uid"],
        request.level_id,
        request.potions,
        request.bloques_utilizados
    )
    
    # Endpoint para obtener estadísticas del nivel (nueva función)
@router.get("/level-statistics/{level_id}", 
            summary="Obtiene estadísticas de un nivel", 
            description="Devuelve estadísticas sobre cuántos usuarios han completado el nivel y su puntuación promedio")
async def get_level_statistics(
    level_id: int,
    authorization: Optional[str] = Header(None)
):
    """
    Obtiene estadísticas de un nivel específico.
    
    - Requiere autenticación mediante token Bearer
    - Devuelve información como intentos totales, usuarios que lo completaron,
      estrellas promedio y cuántos obtuvieron 3 estrellas
    - Útil para análisis y mejoras del juego
    """
    # Validacion del token de autenticación
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    
    # Verificar si es administrador
    # is_admin = await AuthService.is_admin(decoded_token["uid"])
    # if not is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Solo administradores pueden ver estadísticas"
    #     )
    
    # Obtener estadísticas del nivel
    return await GameService.get_level_statistics(level_id)
