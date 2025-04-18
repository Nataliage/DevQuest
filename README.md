# proyectofinal-24-25-grupo_16


# DevQuest API

### Descripción

DevQuest API es el backend desarrollado en FASTAPI para la aplicación DevQuest, orientada a gestionar la autenticación de niveles, registro de progreso y lógica del juego. Se integra con Firebase Admin SDK para la autenticación y el manejo de dtos en Firestore.

##Características 

- **Autenticación:** Registra usuarios y verifica tokens usando Firebase.
- **Gestión de niveles:** Consulta, crea y administra niveles del juego. Los niveles incluyen datos como nombre, descripción, dificultad y puntuación máxima.
- **Registro de progreso:** Guarda y consulta el progreso del usuario en cada nivel.
- **Lógica del juego:** Valida el código enviado por el usuario, guarda estados de nivel, controla la salida del juego y evalúa niveles de pociones.
- **CORS configurado:** Permite solicitudes desde dominios específicos, facilitando la integración con el frontend.
- **Integración con Firebase:** Utiliza Firestore para almacenamiento de datos y Firebase Admin para la autenticación.

## Estructura del Proyecto

La estructura del proyecto se organiza de la siguiente manera:

```bash

project/
├── app/
│   ├── auth/
│   │   ├── routes.py         # Rutas de autenticación
│   │   ├── service.py        # Lógica de autenticación (verificación de tokens, creación de usuarios, etc.)
│   │   └── schemas.py        # Esquemas (modelos) de usuario
│   ├── levels/
│   │   ├── routes.py         # Rutas para la gestión de niveles
│   │   ├── service.py        # Lógica de creación y consulta de niveles
│   │   └── schemas.py        # Esquemas de niveles
│   ├── progress/
│   │   └── routes.py         # Rutas para registrar y consultar el progreso del usuario
│   ├── game/
│   │   ├── routes.py         # Endpoints para la lógica del juego: validación de código, estado de nivel y niveles de pociones
│   │   └── service.py        # Lógica de validación y manejo del juego
│   └── config/
│       └── firebase.py       # Configuración del Firebase Admin SDK y conexión con Firestore
├── main.py                   # Punto de entrada de la aplicación, configuración de CORS e inclusión de routers
└── serviceAccountKey.json    # Archivo de credenciales de Firebase (no olvides proteger este archivo)

```

## Instalación

Asegúrate de contar con Python 3.8+ instalado.

1. Clonar el repositorio:
- git clone https://tu-repositorio-url.git
- cd tu-repositorio

2. Instalar las dependencias:
- pip install -r requirements.txt

3. Configurar Firebase:
- Coloca el archivo serviceAccountKey.json en la raíz del proyecto.
- Verifica que el archivo contenga las credenciales necesarias para inicializar el Firebase Admin SDK.

4. Configurar CORS (opcional):
- En main.py se ha configurado CORS para permitir solicitudes desde http://localhost:8000 y https://www.devquestgame.app. Modifica estas URLs si es necesario.

5. Ejecución: 
- Para iniciar el servidor de desarrollo, utiliza Uvicorn: uvicorn main:app --reload
- Accede a la documentación interactiva en: http://localhost:8000/docs

## Endpoints principales

- Autenticación:

POST /auth/register:
Registra un nuevo usuario.
Payload esperado:  
{
    "email": "usuario@example.com",
    "password": "tu_contraseña",
    "username": "tu_usuario"
}

POST /auth/verify-token:
Verifica la validez del token enviado en el header.
Header requerido:
Authorization: Bearer <token>

- Gestión de niveles:

GET /levels:
Consulta todos los niveles disponibles.

GET /levels/{level_id}:
Consulta la información de un nivel específico.

POST /levels:
Crea un nuevo nivel (solo administradores).
Nota: Se requiere token válido de un usuario con permisos de administrador.

- Progreso del usuario: 

GET /progress:
Obtiene el progreso del usuario autenticado.
Header requerido:
Authorization: Bearer <token>

POST /progress:
Registra el progreso del usuario en un nivel.
Payload esperado:

{
    "level_id": 1,
    "score": 100
}

- Lógica de juego: 

POST /game/validate-code:
Valida el código proporcionado por el usuario y devuelve si es correcto, la puntuación obtenida y un mensaje de retroalimentación.
Payload esperado:

{
    "level_id": 1,
    "code": "correcto",
    "script": {}  // Información adicional para la validación
}

POST /game/save-level-state:
Guarda el estado actual de un nivel.

POST /game/exit:
Marca que el usuario ha salido del juego.

POST /game/validate-potion-level:
Valida el nivel basado en pociones, retornando estrellas, mensajes y otros datos relacionados con la validación.

- Tecnologías utilizadas:

FastAPI: Framework para construir APIs modernas de Python.

Firebase Admin SDK: Para la autenticación y manejo de datos en Firestore.

Pydantic: Validación y serialización de datos.

Uvicorn: Servidor ASGI para ejecutar la aplicación.

Python: Lenguaje de programación utilizado.

- Contribución: 

Para aportar al proyecto, sigue estos pasos:

1. Haz un fork del repositorio.

2. Crea una rama para tu feature:

git checkout -b feature/nueva-funcionalidad

3. Realiza tus cambios y haz commit:

git commit -am 'Agrega nueva funcionalidad'

4. Sube tu rama:

git push origin feature/nueva-funcionalidad

5. Abre un Pull Request para revisar tus cambios.

## Licencia 
## Contacto 

Para dudas o más información, puedes contactar al autor o al equipo de desarrollo a través de: 
