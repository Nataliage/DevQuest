from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional, Dict
from .schemas import Level, LevelCreate, LevelResponse, LevelWithCompletion
from .service import LevelService
from ..auth.service import AuthService
from app.progress.service import ProgressService

router = APIRouter(prefix="/levels", tags=["Levels"])

@router.get("/", response_model=List[LevelWithCompletion], summary="Obtener todos los niveles")
async def get_levels(authorization: Optional[str] = Header(None)):
    """
    Obtiene la lista completa de niveles disponibles y añade el estado 'isCompleted' por usuario.
    Args:
        authorization (str, optional): Token JWT Bearer para identificar al usuario.
    Returns:
        List[LevelWithCompletion]: Lista de niveles con flag isCompleted.
    """ 
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    uid = decoded_token["uid"]

    # Obtener todos los niveles
    levels = await LevelService.get_all_levels()
    print("Niveles obtenidos:", levels)

    # Obtener niveles completados por el usuario
    completed_levels = await ProgressService.get_levels_completed_by_user(uid) or []

    # Añadir isCompleted a cada nivel
    levels_with_status = []
    for lvl in levels:
        level_dict = dict(lvl) if not isinstance(lvl, dict) else lvl
        if "commands" not in level_dict:
            raw_cmds = level_dict.get("listCommands", {})
            commands = []
            for key, val in raw_cmds.items():
                if isinstance(val, dict):
                    commands.extend(val.values())
                else:
                    commands.append(val)
            level_dict["commands"] = commands
        level_dict["isCompleted"] = level_dict.get("level_id") in completed_levels
        levels_with_status.append(level_dict)

    return levels_with_status
@router.get("/{level_id}", response_model=LevelResponse, summary="Obtener detalles de un nivel")
async def get_level(level_id: int, authorization: Optional[str] = Header(None)):
    """
    Obtiene información detallada de un nivel específico, incluyendo configuración de pociones
    y comandos esperados.
    Args:
        level_id (int): ID del nivel a consultar.
        authorization (str, optional): Token JWT en el header Authorization (Bearer).
    Raises:
        HTTPException 401: Si no se proporciona o es inválido el token.
        HTTPException 404: Si el nivel no existe.
    Returns:
        LevelResponse: Detalles del nivel, configuración y comandos esperados.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )   
    try:
        token = authorization.split("Bearer ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato del token incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    decoded_token = await AuthService.verify_token(token)
    level = await LevelService.get_level_by_id(level_id)
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nivel no encontrado"
        )
    #extraer y poner comandos desde listcommands
    raw_cmds: Dict = level.get("listCommands", {})
    commands: List[str] = []
    for key, val in raw_cmds.items():
        if isinstance(val, dict):
            commands.extend(val.values())
        else:
            commands.append(val)
    return LevelResponse(
        level_id=level.get("level_id"),
        name=level.get("name"),
        description=level.get("description"),
        #difficulty=level.get("difficulty"),
        max_score=level.get("max_score"),
        order=level.get("order"),
        estimated_time=level.get("estimated_time"),
        potions_config=level.get("potions_config", {}),
        commands=commands
        )
    #return LevelResponse(
     #   level_id=level.level_id,
     #   name=level.name,
     #   description=level.description,
     #   max_score=level.max_score,
     #   order=level.order,
     #   estimated_time=level.estimated_time
     #   potions_config=data.get("potions_config", {}),
     #   commands=data.get("commands", [])
    # 

# solo admins pueden crear actualizar niveles
@router.post("/", response_model=Level, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo nivel")
async def create_level(level: LevelCreate, authorization: Optional[str] = Header(None)):
    """
    Crea un nuevo nivel. Solo accesible para usuarios con permisos de administrador.
    Args:
        level (LevelCreate): Datos para crear el nuevo nivel.
        authorization (str, optional): Token JWT en el header Authorization (Bearer).
    Raises:
        HTTPException 401: Si no se proporciona o es inválido el token.
        HTTPException 403: Si el usuario no tiene permisos de administrador.
    Returns:
        Level: Nivel creado con los datos registrados.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )   
    try:
        token = authorization.split("Bearer ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato del token incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    decoded_token = await AuthService.verify_token(token)
    # verificar si el user es admin
    is_admin = await LevelService.is_admin(decoded_token["uid"])
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear niveles"
        )

    new_level = await LevelService.create_level(level)
    return new_level