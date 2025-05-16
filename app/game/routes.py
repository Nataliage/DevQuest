from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel
from app.config.firebase import db
from ..auth.service import AuthService
from .service import GameService
from .schemas import CodeValidationRequest, CodeValidationResponse, LevelStateRequest, CommandLevelRequest, CommandLevelResponse, LevelStatisticsResponse

router = APIRouter(prefix="/game", tags=["Game"])

   
@router.post("/validate-code", response_model=CodeValidationResponse, summary="Validar código de nivel")
async def validate_code_endpoint(request: CodeValidationRequest, authorization: Optional[str] = Header(None)):
    """
    Valida el código proporcionado por el usuario para resolver un nivel.

    Args:
        request (CodeValidationRequest): Datos de la solicitud, que incluyen:
            - level_id: ID del nivel a validar.
            - code: Código enviado por el usuario.
            - script: Script asociado para la validación.
        authorization (str, opcional): Token de autenticación en formato Bearer.

    Returns:
        CodeValidationResponse: Resultado de la validación, que contiene:
            - correct: Indica si el código es correcto.
            - score: Puntuación obtenida.
            - message: Mensaje descriptivo del resultado.
            - script (opcional): Información adicional del script.

    Raises:
        HTTPException:
            - 401 Unauthorized: Si no se proporciona el token o el formato es incorrecto.
              Ejemplo:
                {
                    "detail": "Token no proporcionado o formato incorrecto"
                }
            - 500 Internal Server Error: Si ocurre un error durante la validación.
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

@router.post("/save-level-state", summary="Guardar estado del nivel")
async def save_level_state(request: LevelStateRequest, authorization: Optional[str] = Header(None)):
    """
    Guarda el estado actual del nivel para el usuario.
    Útil para permitir continuar una partida más tarde.
    
    - Requiere autenticación mediante token Bearer
    - Guarda el estado del nivel en la base de datos
    Args:
        request (LevelStateRequest): Contiene level_id y estado serializado.
        authorization (str, optional): Token JWT Bearer para autenticación.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException 401: Token no proporcionado o formato incorrecto.
        HTTPException 500: Error interno al guardar estado.
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

@router.post("/exit", summary="Registrar salida del juego")
async def exit_game(authorization: Optional[str] = Header(None)):
    """
    Registra que el usuario ha salido del juego.
    
    - Requiere autenticación mediante token Bearer
    - Útil para análisis de comportamiento y estadísticas
    Args:
        authorization (str, optional): Token JWT Bearer para autenticación.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException 401: Token no proporcionado o formato incorrecto.
        HTTPException 500: Error al registrar la salida.
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

@router.post("/validate-commands", response_model=CommandLevelResponse, summary="Validar comandos del nivel")
async def validate_commands(
    request: CommandLevelRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Valida si el usuario ha completado correctamente un nivel de pociones.
    
    - Requiere autenticación mediante token Bearer
    - Verifica si los estantes coinciden con lo esperado
    - Evalúa si el número de bloques utilizados es óptimo
    - Asigna 0-3 estrellas según el rendimiento
    Args:
        request (CommandLevelRequest): level_id y lista de comandos.
        authorization (str, optional): Token JWT Bearer para autenticación.

    Returns:
        CommandLevelResponse: Resultado con estrellas, mensaje, progreso y niveles completados.

    Raises:
        HTTPException 401: Token no proporcionado o formato incorrecto.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    uid = decoded_token["uid"]
    
    return await GameService.validate_commands (
        uid=uid,
        level_id=request.level_id,
        commands=request.list_commands
    )
# Endpoint para obtener estadísticas del nivel (nueva función)
@router.get("/level-statistics/{level_id}", response_model=LevelStatisticsResponse, summary="Obtener estadísticas del nivel")            
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
    Args:
        level_id (int): ID del nivel a consultar.
        authorization (str, optional): Token JWT Bearer para autenticación.

    Returns:
        LevelStatisticsResponse: Estadísticas del nivel.

    Raises:
        HTTPException 401: Token no proporcionado o formato incorrecto.
        HTTPException 403: Acceso restringido (comentado para futuras mejoras).
    """
    # Validacion del token de autenticación
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
   #uid = decoded_token["uid"] para limitar el acceso a admins

    #  limitar esto a admins:
    # if not await AuthService.is_admin(uid):
    #     raise HTTPException(status_code=403, detail="Solo administradores pueden ver estadísticas")

    return await GameService.get_level_statistics(level_id)
    
    # Verificar si es administrador
    # is_admin = await AuthService.is_admin(decoded_token["uid"])
    # if not is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Solo administradores pueden ver estadísticas"
    #     )
    
   
