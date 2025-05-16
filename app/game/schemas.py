from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CodeValidationRequest(BaseModel):
    """Modelo para solicitud de validación de código"""
    level_id: int = Field(..., example=1, description="ID del nivel a validar")
    code: str = Field(..., example="print('Hola Mundo')", description="Código enviado por el usuario para validar")
    script: dict = Field(..., description="Script asociado para la validación")

class CodeValidationResponse(BaseModel):
    """Modelo para respuesta de validación de código"""
    correct: bool = Field(..., description="Indica si el código es correcto")
    score: int = Field(..., example=100, description="Puntuación obtenida")
    message: Optional[str] = Field(None, description="Mensaje descriptivo del resultado")
    script: Optional[dict] = Field(None, description="Información adicional del script")

class LevelStateRequest(BaseModel):
    """Modelo para guardar el estado de un nivel"""
    level_id: int = Field(..., example=1, description="ID del nivel")
    state: dict = Field(..., description="Estado serializado del nivel")

class CommandLevelRequest(BaseModel):
    """Modelo para validación de nivel mediante bloques y comandos"""
    level_id: int = Field(..., example=1, description="ID del nivel")
    list_commands: List[str] = Field(..., example=["ESTANTE1", "SALUD", "VENENO"], description="Lista de comandos enviados por el usuario")

class CommandLevelResponse(BaseModel):
    """Modelo para respuesta de validación del nivel"""
    correct: bool = Field(..., description="Indica si el nivel fue completado correctamente")
    stars: int = Field(..., example=3, description="Número de estrellas obtenidas")
    message: str = Field(..., description="Mensaje de retroalimentación")
    progress: List[Dict[str, Any]] = Field(..., description="Lista con el progreso del usuario")
    levels_completed: List[int] = Field(..., description="Lista de IDs de niveles completados")

    
    
class LevelStatisticsResponse(BaseModel):
    """Modelo para respuesta de estadísticas de nivel"""
    total_attempts: int = Field(..., example=10, description="Número total de intentos")
    completed_count: int = Field(..., example=7, description="Cantidad de usuarios que completaron el nivel")
    average_stars: float = Field(..., example=2.5, description="Estrellas promedio obtenidas")
    three_stars_count: int = Field(..., example=3, description="Cantidad de usuarios con 3 estrellas")
    progress: List[Dict[str, Any]] = Field(..., description="Lista con el progreso registrado")
    levels_completed: List[int] = Field(..., description="Lista de niveles completados")