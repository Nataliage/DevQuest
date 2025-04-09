from fastapi import HTTPException, status
from app.config.firebase import db


class LevelService:
    @staticmethod
    async def get_all_levels():
        try:
            levels_ref = db.collection('levels')
            levels = levels_ref.order_by('order').get()
            return [
                {
                    "level_id": level.id,
                    **level.to_dict()
                } for level in levels
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener niveles: {str(e)}"
            )
            
    @staticmethod
    async def get_level_by_id(level_id: int):
        try:
            level_ref = db.collection('levels').document(str(level_id))
            level = level_ref.get()
            if not level.exists:
                return None
            return {
                "level_id": level.id,
                **level.to_dict()
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener nivel: {str(e)}"
            )
    
    @staticmethod
    async def is_admin(uid: str):
        try:
            # Aquí asumimos que tienes una colección de administradores
            admin_ref = db.collection('users').document(uid)
            admin = admin_ref.get()
            if not admin.exists:
                return False
            
            # Verificar si el usuario tiene rol de administrador
            return admin.get('role') == 'admin'
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al verificar permisos: {str(e)}"
            )            
    @staticmethod
    async def create_level(level):
        try:
            levels_ref = db.collection('levels')
            # Obtener todos los niveles para determinar el máximo level_id actual
            levels = levels_ref.get()
            max_id = 0
            for doc in levels:
                data = doc.to_dict()
                if 'level_id' in data and isinstance(data['level_id'], int):
                    if data['level_id'] > max_id:
                        max_id = data['level_id']
            new_id = max_id + 1

            new_level_data = level.dict()
            # Agregar el campo level_id
            new_level_data['level_id'] = new_id

            # Crear el documento con el id generado (convertido a cadena)
            levels_ref.document(str(new_id)).set(new_level_data)

            return new_level_data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear el nivel: {str(e)}"
            )