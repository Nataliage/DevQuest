
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.levels.routes import router as levels_router
from app.progress.routes import router as progress_router
from app.game.routes import router as game_router
# Cargar variables de entorno desde el archivo .env

from dotenv import load_dotenv

load_dotenv()
#from app.config.firebase import firebase_app


app = FastAPI(title="DevQuest API", description="Backend API for DevQuest application", version= "1.0.0", docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://www.devquestgame.app"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
#registrar los routers de cada modulo de la aplicacion
#app.include_router(auth_router, tags=["Authentication"])
#app.include_router(levels_router, tags=["Levels"])
#app.include_router(progress_router, tags=["Progress"])
#app.include_router(game_router, tags=["Game"])

#app.include_router(auth_router)   
#app.include_router(levels_router)
#app.include_router(progress_router)
#app.include_router(game_router)

#endpoint raíz para verificar que la API funciona

app.include_router(auth_router,     prefix="/api")
app.include_router(levels_router,   prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(game_router,     prefix="/api")
@app.get("/api",  include_in_schema=False)
@app.get("/api/", include_in_schema=False)
def read_root():
    """
    Endpoint raíz que confirma que la API está en funcionamiento.
    Proporciona información básica y enlace a la documentación.
    """    
    return JSONResponse({
        "message": "Bienvenido a la API de DevQuest",
        "version": "1.0.0",
        "docs": "/api/docs"
    })