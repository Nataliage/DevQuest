from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProgressBase(BaseModel):
    level_id: int
    score: int    
#registro de progress 
class ProgressCreate(ProgressBase):
    pass
#progress que se devuelve en las respuestas
class Progress(ProgressBase):
    progress_id: str  
    user_id: str
    start_date: datetime
    completion_date: Optional[datetime] = None

    class Config:
        orm_mode = True 