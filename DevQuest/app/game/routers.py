from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from pydantic import BaseModel
from ..auth.service import AuthService
from .service import GameService

router = APIRouter(prefix="/game", tags=["Game"])

class CodeValidationRequest(BaseModel):
    level_id: int
    code: str

class CodeValidationResponse(BaseModel):
    correct: bool
    score: int
    message: Optional[str] = None

@router.post("/validate-code", response_model=CodeValidationResponse)
async def validate_code_endpoint(request: CodeValidationRequest, authorization: Optional[str] = Header(None)):
    # Validación del token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)

    # Llamada al servicio para validar el código
    return await GameService.validate_code(decoded_token["uid"], request.level_id, request.code)

class LevelStateRequest(BaseModel):
    level_id: int
    state: dict

@router.post("/save-level-state")
async def save_level_state(request: LevelStateRequest, authorization: Optional[str] = Header(None)):
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
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto"
        )
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)

    await GameService.exit_game(decoded_token["uid"])
    return {"detail": "Juego finalizado correctamente"}
