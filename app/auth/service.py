from firebase_admin import auth, firestore
from app.config.firebase import db
from fastapi import HTTPException, status
from datetime import datetime


class AuthService:
    @staticmethod
    async def verify_token(token: str): 
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
        try:
            user = auth.get_user_by_email(email)
            return user
        except:
            return None
    
    @staticmethod
    async def create_user(email: str, password: str, display_name: str):
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
                "last_login": datetime.utcnow()
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
        try:
            db.collection('users').document(uid).update({
                "last_login": datetime.utcnow()
            })
        except Exception as e:
            # Solo log, no interrumpir el flujo
            print(f"Error updating last login: {str(e)}")