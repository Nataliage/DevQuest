import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import logging #libreria logs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    certificate_path = "serviceAccountKey.json"
    if not os.path.exists(certificate_path):
        raise FileNotFoundError(f"No se encontró el archivo de certificado: {certificate_path}")
    
    cred = credentials.Certificate(certificate_path)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    logger.info("Firebase Admin SDK inicializado correctamente.")
except Exception as e:
    logger.error(f"Error al inicializar Firebase Admin SDK: {e}")
    raise

def get_auth():
    return auth