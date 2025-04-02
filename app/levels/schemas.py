from pydantic import BaseModel

class LevelBase(BaseModel):
    name: str
    description: str
    difficulty: int
    max_score: int
    order: int
    estimated_time: int

class LevelCreate(LevelBase):
    pass

class Level(LevelBase):
    level_id: int
    
    class Config:
        orm_mode = True