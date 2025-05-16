from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional, Dict
from .schemas import Level, LevelCreate, LevelResponse
from .service import LevelService
from ..auth.service import AuthService

router = APIRouter(prefix="/levels", tags=["Levels"])

@router.get("/", response_model=List[Level])
async def get_levels(authorization: Optional[str] = Header(None)):  
    levels = await LevelService.get_all_levels()
    return levels
@router.get("/{level_id}", response_model=LevelResponse)
async def get_level(level_id: int, authorization: Optional[str] = Header(None)):
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
        difficulty=level.get("difficulty"),
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
@router.post("/", response_model=Level, status_code=status.HTTP_201_CREATED)
async def create_level(level: LevelCreate, authorization: Optional[str] = Header(None)):
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