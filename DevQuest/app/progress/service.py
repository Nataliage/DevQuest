from app.config.firebase import db
from fastapi import HTTPException, status
from datetime import datetime



class ProgressService:
    @staticmethod
    async def get_user_progress(user_id: str):
        try:
            progress_ref = db.collection('progress')
            progress = progress_ref.where("user_id", "==", user_id).get()
            return [
                {
                    "progress_id": doc.id,
                    **doc.to_dict()
                } for doc in progress
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener progreso: {str(e)}"
            )
    
    @staticmethod
    async def record_progress(user_id: str, level_id: int, score: int):
        try:
            # Verificar si ya existe un progreso para este nivel y usuario
            progress_ref = db.collection('progress')
            existing_progress = progress_ref.where("user_id", "==", user_id)\
                                          .where("level_id", "==", level_id)\
                                          .get()
            
            now = datetime.utcnow()
            
            if len(existing_progress) > 0:
                # Actualizar progreso existente
                progress_id = existing_progress[0].id
                progress_ref.document(progress_id).update({
                    "puntuacion": score,
                    "fecha_completado": now
                })
                
                # Obtener el documento actualizado
                updated_doc = progress_ref.document(progress_id).get()
                return {
                    "progress_id": progress_id,
                    **updated_doc.to_dict()
                }
            else:
                # Crear nuevo progreso
                new_progress = {
                    "user_id": user_id,
                    "level_id": level_id,
                    "score": score,
                    "start_date": now,
                    "completion_date": now
                }
                
                new_doc = progress_ref.add(new_progress)[1]
                progress_id = new_doc.id
                
                return {
                    "progress_id": progress_id,
                    **new_progress
                }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar progreso: {str(e)}"
            )