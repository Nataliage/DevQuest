import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import logging #libreria logs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    #ruta al archivo de credenciales de Firebase
    certificate_path = "serviceAccountKey.json"
    #verificar que el archivo existe
    if not os.path.exists(certificate_path):
        raise FileNotFoundError(f"No se encontró el archivo de certificado: {certificate_path}")
    #carga credenciales
    cred = credentials.Certificate(certificate_path)
    #inicializar la app de Firebase si no esta incializada
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    #obtener cliente de Firestore
    db = firestore.client()
    logger.info("Firebase Admin SDK inicializado correctamente.")
except Exception as e:
    logger.error(f"Error al inicializar Firebase Admin SDK: {e}")
    raise

def get_auth():
    """
    Obtiene la instancia de autenticación de Firebase.
    
    Returns:
        El cliente de autenticación de Firebase para operaciones como
        verificación de tokens, creación de usuarios, etc.
    """
    return auth