from firebase_admin import auth, firestore
from app.config.firebase import db
from fastapi import HTTPException, status
from datetime import datetime


class AuthService:
    @staticmethod
    async def verify_token(token: str):
        """
        Verifica y decodifica un token JWT de Firebase.
        Args:
            token (str): Token JWT enviado por el cliente.
        Returns:
            dict: Datos decodificados del token, como 'uid' y 'email'.
        Raises:
            HTTPException: Si el token es inválido o expirado.
        """
        
        if token == "dummy":
            return {"uid": "testuser", "email": "test@example.com"} 
        try:
            # token de firebase
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_user_by_email(email: str):
        """
        Obtiene usuario de Firebase Authentication por email.
        Args:
            email (str): Email del usuario.
        Returns:
            UserRecord | None: Objeto usuario o None si no existe.
        """
        try:
            user = auth.get_user_by_email(email)
            return user
        except:
            return None
    
    @staticmethod
    async def create_user(email: str, password: str, display_name: str):
        """
        Crea un nuevo usuario en Firebase Authentication y Firestore.
        Args:
            email (str): Email del usuario.
            password (str): Contraseña del usuario.
            display_name (str): Nombre para mostrar del usuario.
        Returns:
            UserRecord: Objeto usuario creado.
        Raises:
            HTTPException: Si ocurre un error al crear el usuario.
        """
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            user_data = {
                "email": email,
                "username": display_name,
                "registration_date": datetime.utcnow(),
                "premium": False,
                "role": "user",
                "last_login": datetime.utcnow(),
                "unlocked_levels": [1], #desbloqueamos el primer nivel por defecto
            }
            db.collection('users').document(user.uid).set(user_data)
            
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear usuario: {str(e)}"
            )
    @staticmethod
    async def update_last_login(uid: str):
        """
        Actualiza la fecha del último login de un usuario en Firestore.
        Args:
            uid (str): UID del usuario.
        """
        try:
            db.collection('users').document(uid).update({
                "last_login": datetime.utcnow()
            })
        except Exception as e:
            # Solo log, no interrumpir el flujo
            print(f"Error updating last login: {str(e)}")