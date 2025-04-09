from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.levels.routes import router as levels_router
from app.progress.routes import router as progress_router
from app.game.routes import router as game_router
#from app.config.firebase import firebase_app


app = FastAPI(title="DevQuest API", description="Backend API for DevQuest application", version= "1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://www.devquestgame.app"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
#registrar los routers de cada modulo de la aplicacion
app.include_router(auth_router)
app.include_router(levels_router)
app.include_router(progress_router)
app.include_router(game_router)

#endpoint raíz para verificar que la API funciona
@app.get("/")
def read_root():
    """
    Endpoint raíz que confirma que la API está en funcionamiento.
    Proporciona información básica y enlace a la documentación.
    """    
    return {"message": "Bienvenido a la API de DevQuest",
            "version": "1.0.0",
            "docs": "/docs"
            }