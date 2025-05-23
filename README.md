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
│   │   ├── service.py        # Lógica de autenticación y manejo de usuarios
│   │   └── schemas.py        # Modelos de datos para autenticación
│   ├── levels/
│   │   ├── routes.py         # Rutas para gestión de niveles
│   │   ├── service.py        # Lógica de consulta y creación de niveles
│   │   └── schemas.py        # Modelos de datos para niveles
│   ├── progress/
│   │   ├── routes.py         # Rutas para progreso de usuario
│   │   ├── service.py        # Lógica para registrar y consultar progreso
│   │   └── schemas.py        # Modelos de datos para progreso
│   ├── game/
│   │   ├── routes.py         # Rutas para lógica de juego y validaciones
│   │   ├── service.py        # Lógica de validación de comandos, código, estados
│   │   └── schemas.py        # Modelos de datos para validaciones
│   └── config/
│       └── firebase.py       # Configuración Firebase Admin SDK y conexión Firestore
├── main.py                   # Punto de entrada y configuración FastAPI (CORS, routers)
└── serviceAccountKey.json    # Credenciales Firebase (NO compartir públicamente)
    # Archivo de credenciales de Firebase (proteger archivo)

```

## Instalación

Asegúrate de contar con Python 3.8+ instalado.

1. Clonar el repositorio:
- git clone https://tu-repositorio-url.git
- cd tu-repositorio
- crear entorno virtual python -m venv .venv source .venv/bin/activate o .venv\Scripts\activate en Windows
2. Instalar las dependencias:
- pip install -r requirements.txt

3. Configurar Firebase:
- Coloca el archivo serviceAccountKey.json en la raíz del proyecto.
- Verifica que el archivo contenga las credenciales necesarias para inicializar el Firebase Admin SDK.

4. Configurar CORS (opcional):
- En main.py se ha configurado CORS para permitir solicitudes desde http://localhost:8000 y https://www.devquestgame.app. Modifica estas URLs si es necesario.

5. Ejecución: 
- Para iniciar el servidor de desarrollo, utiliza Uvicorn: uvicorn main:app --reload
- Accede a la documentación interactiva en: http://localhost:8000/api/docs

## Endpoints principales

- Autenticación:

POST /auth/register:
Registra y hace login a un nuevo usuario 
Payload esperado:  
{
    "email": "usuario@example.com",
    "password": "tu_contraseña",
    "username": "tu_usuario"
}
Responde con token JWT y datos del usuario.

POST /auth/verify-token:
Verifica la validez del token enviado en el header.
Header requerido:
Authorization: Bearer <token>

- Gestión de niveles:

GET /levels:
Consulta todos los niveles disponibles. 
Obtiene lista completa de niveles con flag isCompleted para indicar niveles completados por usuario.

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

Python 3.8+: Lenguaje de programación utilizado.
- Pruebas:

Se dispone de tests automáticos unitarios e integración para la mayoría de funcionalidades clave.

La API ha sido probada manualmente con Postman en entornos local y producción.

Documentación Swagger auto-generada para facilitar la integración.

- Futuras mejoras:

Mejorar la validación lógica en niveles 

Implementar interfaz de usuario para administración de niveles.

Añadir lógica avanzada con IA para evaluación de código y comandos.

Mejoras en la experiencia del usuario y seguridad.


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
