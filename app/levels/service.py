from fastapi import HTTPException, status
from app.config.firebase import db


class LevelService:
    @staticmethod
    async def get_all_levels():
        """
        Obtiene todos los niveles ordenados por su campo 'order'.
        Returns:
            List[dict]: Lista de niveles con sus datos y su ID.        
        Raises:
            HTTPException: Error interno en caso de fallo al obtener datos.
        """
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
        """
        Obtiene un nivel específico mediante su level_id.
        Args:
            level_id (int): Identificador del nivel a buscar.
        Returns:
            dict | None: Datos del nivel si existe, None si no se encuentra.
        Raises:
            HTTPException: Error interno en caso de fallo al consultar.
        """
        try:
            query = db.collection("levels").where("level_id", "==", level_id).limit(1).get()
            if not query:
                return None
            return query[0].to_dict()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener nivel: {str(e)}"
            )
    
    @staticmethod
    async def is_admin(uid: str):
        """
        Verifica si un usuario tiene rol de administrador.
        Args:
            uid (str): ID del usuario a verificar.
        Returns:
            bool: True si es admin, False en caso contrario.
        Raises:
            HTTPException: Error interno en caso de fallo al consultar.
        """
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
        """
        Crea un nuevo nivel asignándole un level_id secuencial único.
        Args:
            level (LevelCreate): Modelo con datos del nuevo nivel.
        Returns:
            dict: Datos del nivel creado, incluyendo level_id asignado.
        Raises:
            HTTPException: Error interno en caso de fallo al crear el nivel.
        """
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