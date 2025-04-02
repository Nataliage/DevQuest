from app.config.firebase import db
from fastapi import HTTPException, status
from datetime import datetime



class GameService:
    @staticmethod
    async def validate_code(uid: str, level_id: int, code: str):
        # Ejemplo simple de validacion de codigo
        if code == "correcto":
            return {
                "correct": True,
                "score": 100,
                "message": "¡Excelente! Código correcto."
            }
        else:
            return {
                "correct": False,
                "score": 0,
                "message": "Código incorrecto, inténtalo de nuevo."
            }

    @staticmethod
    async def save_level_state(uid: str, level_id: int, state: dict):
        # Guarda el estado del nivel en Firestore
        try:
            doc_id = f"{uid}_{level_id}"
            doc_ref = db.collection('level_states').document(doc_id)
            doc_ref.set({
                "uid": uid,
                "level_id": level_id,
                "state": state,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar el estado: {str(e)}"
            )

    @staticmethod
    async def exit_game(uid: str):
        # Logica para marcar que el usuario salio del juego
        try:
            sessions_ref = db.collection('game_sessions')
            sessions_ref.document(uid).set({
                "exit": True,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al salir del juego: {str(e)}"
            )
