from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CodeValidationRequest(BaseModel):
    """Modelo para solicitud de validación de código"""
    level_id: int
    code: str
    script: dict

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

class CommandLevelRequest(BaseModel):
    """Modelo para validación de nivel mediante bloques y comandos"""
    level_id: int
    list_commands: List[str]

class CommandLevelResponse(BaseModel):
    """Modelo para respuesta de validación del nivel"""
    correct: bool
    stars: int
    message: str
    progress: List[Dict[str, Any]]
    levels_completed: List[int]
    
    
class LevelStatisticsResponse(BaseModel):
    """Modelo para respuesta de estadísticas de nivel"""
    total_attempts: int
    completed_count: int
    average_stars: float
    three_stars_count: int
    progress: List[Dict[str, Any]]
    levels_completed: List[int]