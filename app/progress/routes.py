from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .service import ProgressService
from ..auth.service import AuthService

router = APIRouter(prefix="/progress", tags=["Progress"])
class ProgressBase(BaseModel):
    level_id: int
    score: int    
class ProgressCreate(ProgressBase):
    pass

class Progress(ProgressBase):
    progress_id: int
    user_id: str
    start_date: datetime
    completion_date: Optional[datetime] = None
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[Progress])
async def get_user_progress(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    
    user_progress = await ProgressService.get_user_progress(decoded_token["uid"])
    return user_progress

@router.post("/", response_model=Progress, status_code=status.HTTP_201_CREATED)
async def record_progress(progress: ProgressCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado o formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split("Bearer ")[1]
    decoded_token = await AuthService.verify_token(token)
    
    new_progress = await ProgressService.record_progress(
        user_id=decoded_token["uid"],
        level_id=progress.level_id,
        score=progress.score
    )
    return new_progress

