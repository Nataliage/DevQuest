from pydantic import BaseModel
from typing import List, Dict, Optional

class LevelResponse(BaseModel):
    level_id: int
    name: str
    description: str
    #difficulty: int
    max_score: int
    order: Optional[int] = None
    estimated_time: Optional[int] = None   
    potions_config: Dict[str, int]
    commands: List[str]


class LevelBase(BaseModel):
    name: str
    description: str
    #difficulty: int
    max_score: int
    order: int
    estimated_time: int

class LevelCreate(LevelBase):
    pass

class Level(LevelBase):
    level_id: int
    
    class Config:
        orm_mode = True
        