from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class LevelResponse(BaseModel):
    level_id: int = Field(..., example=1, description="ID único del nivel")
    name: str = Field(..., example="Nivel 1: Introducción", description="Nombre del nivel")
    description: str = Field(..., example="Primer nivel para familiarizarse con los controles", description="Descripción del nivel")
    #difficulty: int = Field(..., example=1, description="Nivel de dificultad (opcional)")
    max_score: int = Field(..., example=100, description="Puntuación máxima del nivel")
    order: Optional[int] = Field(None, example=1, description="Orden de aparición del nivel")
    estimated_time: Optional[int] = Field(None, example=15, description="Tiempo estimado para completar el nivel en minutos")   
    potions_config: Dict[str, int] = Field(..., example={"pocion_vida": 3, "pocion_mana": 2}, description="Configuración de pociones necesarias para el nivel")
    commands: List[str] = Field(..., example=["ESTANTE1", "SALUD", "VENENO"], description="Lista de comandos esperados para el nivel")


class LevelBase(BaseModel):
    name: str = Field(..., example="Nivel 1: Introducción", description="Nombre del nivel")
    description: str = Field(..., example="Primer nivel para familiarizarse con los controles", description="Descripción del nivel")
    #difficulty: int = Field(..., example=1, description="Nivel de dificultad")
    max_score: int = Field(..., example=100, description="Puntuación máxima del nivel")
    order: int = Field(..., example=1, description="Orden de aparición del nivel")
    estimated_time: int = Field(..., example=15, description="Tiempo estimado para completar el nivel en minutos")
class LevelCreate(LevelBase):
    pass
class LevelWithCompletion(BaseModel):
    level_id: int = Field(..., example=1, description="ID único del nivel")
    name: str = Field(..., example="Nivel 1: Introducción")
    description: str = Field(..., example="Primer nivel para familiarizarse con los controles")
    max_score: int = Field(..., example=100)
    order: Optional[int] = Field(None, example=1)
    estimated_time: Optional[int] = Field(None, example=15)
    potions_config: Dict[str, int] = Field(...)
    commands: List[str] = Field(...)
    isCompleted: bool = Field(..., description="Indica si el usuario completó este nivel")
    class Config:
        orm_mode = True
class Level(LevelBase):
    level_id: int = Field(..., example=1, description="ID único del nivel")
    
    class Config:
        orm_mode = True
        