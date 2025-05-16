from fastapi import HTTPException, status
from app.config.firebase import db
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class GameService:
    """
    Servicio que gestiona la logica del juego, incluyendo validacion de niveles, 
    guardado de progreso y gestion de sesiones
    """
    @staticmethod
    async def validate_commands(uid: str, level_id: int, commands: List[str]):
        """
        Valida si el usuario ha completado correctamente un nivel de comandos.
        
        Args:
            uid (str): ID del usuario
            level_id (int): ID del nivel
            commands (List[str]): Lista de comandos enviados por el usuario
            
        Returns:
            dict: Resultado de la validacion con estrellas obtenidas y feedback 
        
        """
        #1. Verfiicar si el nivel está desbloqueado
        user_doc = db.collection("users").document(uid).get()
        user_data = user_doc.to_dict()
        unlocked = user_data.get("unlocked_levels", [])
        
        if level_id not in unlocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nivel no desbloqueado"
            )
        #2. Cargar datos del nivel desde Firestore
         #obtener el nivel del usuario desde Firestore
        level_doc = db.collection("levels").document(f"Level{level_id}").get()
        if not level_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nivel no encontrado"
            )
        level_data = level_doc.to_dict()
        list_commands = level_data.get("listCommands", {})
    
        #comandos esperados
        
        expected_commands = set()
        if "ESTANTE" in list_commands:
            expected_commands.update(list_commands["ESTANTE"].values())
        for key, value in list_commands.items():
            if key != "ESTANTE":
                expected_commands.add(value)
        received_commands = set(commands) 
                
        #starts
        if received_commands == expected_commands:
            stars = 3
            message = "¡Perfecto! Has utilizado exactamente los comandos requeridos."
        elif expected_commands.issubset(received_commands):
            stars = 2
            message = "¡Bien! Has usado todos los comandos correctos, pero también algunos de más."
        elif received_commands & expected_commands:
            stars = 1
            message = "Has acertado algunos comandos, pero te faltan otros."
        else:
            stars = 0
            message = "Comandos incorrectos. Inténtalo de nuevo."

        correct = stars > 0
 
        # guardar el progreso del usuario si es correcto
        if correct:
            now = datetime.utcnow()
            db.collection("progress").add({
                "user_id": uid,
                "level_id": level_id,
                "stars": stars,
                "start_date": now,
                "completion_date": now,
            })
            # Desbloqueamos el siguiente nivel
            next_level_id = level_id + 1
            if next_level_id not in unlocked:
                unlocked.append(next_level_id)
                db.collection("users").document(uid).update({
                    "unlocked_levels": unlocked
                })
                
    
        #obtener el progreso del usuario actualizado    
        progress_docs = db.collection("progress").where("user_id", "==", uid).stream()
        progress = [doc.to_dict() for doc in progress_docs]
        levels_completed = [p["level_id"] for p in progress if "level_id" in p]
    
        #devolver la respuesta
        return {
            "correct": correct,
            "stars": stars,
            "message": "¡Perfecto!" if stars == 3 else  "¡Bien!" if stars == 2 else "¡Sigue intentándolo!",
            "progress": progress,
            "levels_completed": levels_completed,
        }
        
    @staticmethod    
    async def validate_code(uid: str, level_id: int, code: str, script: dict):
       
        
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
        """
        Guarda el estado actual del nivel para permitir continuar mas tarde. 
        
        Args:
            uid (str): ID del usuario
            level_id (int): ID del nivel
            state (dict): Estado del nivel a guardar
            
        Raises:
            HTTPException: Si ocurre un error al guardar el estado
        """
        logger.info(f"Guardando estado del nivel {level_id} para usuario {uid}")
        # Guarda el estado del nivel en Firestore
        try:
            doc_id = f"{uid}_{level_id}"
            doc_ref = db.collection('level_states').document(doc_id)
            #guardar estado con timestamp
            doc_ref.set({
                "uid": uid,
                "level_id": level_id,
                "state": state,
                "timestamp": datetime.utcnow()
            })
            logger.info(f"Estado guardado correctamente para usuario {uid} en nivel {level_id}")
        except Exception as e:
            logger.error(f"Error guardando estado: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar el estado: {str(e)}"
            )

    @staticmethod
    async def exit_game(uid: str):
        """
        Marca que el usuario ha salido del juego, util para analisis y estadisticas.
        
        Args:
            uid (str): ID del usuario que sale del juego
            
        Raises:
            HTTPException: Si ocurre un error al registrar la salida 
        
        """
        logger.info(f"Usuario {uid} saliendo del juego")
        # registrar salida en la coleccion de sesiones
        try:
            sessions_ref = db.collection('game_sessions')
            sessions_ref.document(uid).set({
                "exit": True,
                "timestamp": datetime.utcnow()
            })
            logger.info(f"Salida registrada correctamente para usuario {uid}")
        except Exception as e:
            logger.error(f"Error registrando salida: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al salir del juego: {str(e)}"
            )

    @staticmethod
    async def validate_potion_level(uid: str, level_id: int, potions: Dict[str, int], bloques_utilizados: List[str]):
        """
        Valida si el usuario ha completado correctamente un nivel de pociones.
        Verifica si las cantidades de pociones coinciden con lo esperado y si se utilizó el numero optimo de bloques.
        
        Args:
            uid (str): ID del usuario
            level_id (int): ID del nivel de pociones
            potions (Dict[str, int]): Diccionario con las cantidades de cada tipo de poción
            bloques_utilizados (List[str]): Lista de bloques utilizados en la solución
            
        Returns:
            dict: Resultado de la validacion con estrellas obtenidas y feedback 
        
        """
        logger.info(f"Validando nivel de pociones {level_id} para usuario {uid}")
        try:
            # Obtener configuracion del nivel desde Firestore
            level_ref = db.collection('levels').document(f"Level{level_id}")
            level_doc = level_ref.get()
            
            if not level_doc.exists:
                logger.warning(f"Nivel {level_id} no encontrado")
                return {
                    "correct": False,
                    "stars": 0,
                    "message": "Nivel no encontrado",
                    "pociones_correctas": 0,
                    "total_pociones": 0,
                    "bloques_utilizados": len(bloques_utilizados),
                    "bloques_optimales": 0
                }
            #extraer configuracion del nivel
            
            level_data = level_doc.to_dict()
            expected_potions = level_data.get('potions_config', {})
            perfect_score = level_data.get('perfect_score', 3)  # bloques ideales
            
            # validar pociones
            pociones_correctas = 0
            total_pociones = len(expected_potions)
            
            for tipo_pocion, esperado in expected_potions.items():
                actual = potions.get(tipo_pocion, 0)
                if actual == esperado:
                    pociones_correctas += 1
            
            # calcular porcentaje de pociones correctas
            porcentaje_pociones = (pociones_correctas / total_pociones) * 100 if total_pociones > 0 else 0
            
            # verificar cantidad de bloques utilizados
            num_bloques = len(bloques_utilizados)
            
            # determinar estrellas
            stars = 0
            if porcentaje_pociones == 100:
                if num_bloques <= perfect_score:
                    stars = 3  # todas las pociones correctas y usando el numero optimo de bloques
                    message = f"¡Perfecto! Has colocado todas las pociones correctamente usando solo {num_bloques} bloques."
                else:
                    stars = 2  # todas las pociones correctas pero usando más bloques de lo ideal
                    message = f"¡Buen trabajo! Has colocado todas las pociones correctamente, pero podrías hacerlo con menos bloques."
            elif porcentaje_pociones >= 50:
                stars = 1  # al menos la mitad de las pociones correctas
                message = f"Has colocado correctamente {pociones_correctas} de {total_pociones} tipos de pociones."
            else:
                stars = 0
                message = "Intenta de nuevo. Revisa la cantidad de cada tipo de poción."
            
            # guardar progreso
            if stars > 0:
                await GameService.save_potion_progress(uid, level_id, stars, potions, bloques_utilizados)
                logger.info(f"Usuario {uid} completó nivel {level_id} con {stars} estrellas")
            else:
                logger.info(f"Usuario {uid} no completó nivel {level_id}")
                #respuesta con detalles del resultado
            return {
                "correct": stars > 0,
                "stars": stars,
                "message": message,
                "pociones_correctas": pociones_correctas,
                "total_pociones": total_pociones,
                "bloques_utilizados": num_bloques,
                "bloques_optimales": perfect_score
            }
        
        except Exception as e:
            logger.error(f"Error en validate_potion_level: {str(e)}")
            return {
                "correct": False,
                "stars": 0,
                "message": f"Error en la validación: {str(e)}",
                "pociones_correctas": 0,
                "total_pociones": 0,
                "bloques_utilizados": len(bloques_utilizados),
                "bloques_optimales": 0
            }
    
    @staticmethod
    async def save_potion_progress(uid: str, level_id: int, stars: int, potions: Dict[str, int], bloques: List[str]):
        """
        Guarda el progreso del usuario en un nivel de pociones.
        Solo actualiza si la nueva puntuación es mejor que la anterior.
        
        Args:
            uid (str): ID del usuario
            level_id (int): ID del nivel
            stars (int): Número de estrellas obtenidas (0-3)
            potions (Dict[str, int]): Cantidades de pociones utilizadas
            bloques (List[str]): Bloques utilizados en la solución
        """
        logger.info(f"Guardando progreso del nivel {level_id} para usuario {uid} con {stars} estrellas")
        
        try:
            #referenciaala coleccion de progress
            progress_ref = db.collection('progress')
            #buscar si existe progreso previo para este usuario y nivel 
            existing = progress_ref.where("user_id", "==", uid).where("level_id", "==", f"level{level_id}").get()
            
            now = datetime.utcnow()
            #preparar datos para guardar
            data = {
                "user_id": uid,
                "level_id": f"level{level_id}",
                "stars": stars,
                "potions": potions,
                "bloques": bloques,
                "completion_date": now
            }
            #actualizar o crear segun corresponda
            if existing:
                # solo actualizar si la puntuacion es mejor
                doc = existing[0]
                current_stars = doc.to_dict().get('stars', 0)
                if stars > current_stars:
                    logger.info(f"Actualizando progreso existente para usuario {uid} en nivel {level_id}")
                    progress_ref.document(doc.id).update(data)
                else:
                    logger.info(f"Manteniendo progreso existente para usuario {uid} en nivel {level_id}")
            else:
                # Crear nuevo registro
                logger.info(f"Creando nuevo progreso para usuario {uid} en nivel {level_id}")
                data["start_date"] = now
                progress_ref.add(data)
                
        except Exception as e:
            logger.error(f"Error guardando progreso: {str(e)}")
    @staticmethod
    async def get_level_statistics(level_id: int):
        """
        Obtiene estadísticas sobre cuántos usuarios han completado el nivel 
        y su puntuación promedio.
        
        Args:
            level_id (int): ID del nivel para obtener estadísticas
            
        Returns:
            dict: Estadísticas del nivel incluyendo intentos, completados y estrellas
        """
        logger.info(f"Obteniendo estadísticas del nivel {level_id}")
        
        
            # inicializar contadores
        stats = {
        "total_attempts": 0,
        "completed_count": 0,
        "average_stars": 0.0,
        "three_stars_count": 0,
        "average_duration_seconds": 0.0,
        }

        try:
            progress_docs = db.collection("progress").where("level_id", "==", level_id).stream()

            total_stars = 0
            total_duration = 0
            duration_entries = 0
            progress_list = []
            levels_completed = []
            found = False  # Indicador de si hubo progreso

            for doc in progress_docs:
                found = True
                data = doc.to_dict()
                progress_list.append(data)

                stats["total_attempts"] += data.get("attempts", 1)
                stars = data.get("stars", 0)

                if stars > 0:
                    stats["completed_count"] += 1
                    total_stars += stars

                if stars == 3:
                    stats["three_stars_count"] += 1

                start = data.get("start_date")
                end = data.get("completion_date")
                if start and end:
                    duration = (end.replace(tzinfo=None) - start.replace(tzinfo=None)).total_seconds()
                    total_duration += duration
                    duration_entries += 1

                if "level_id" in data:
                    levels_completed.append(data["level_id"])

            if not found:
                logger.info(f"No hay datos de progreso para el nivel {level_id}")
                return {
                    **stats,
                    "progress": [],
                    "levels_completed": []
                }

            if stats["completed_count"] > 0:
                stats["average_stars"] = round(total_stars / stats["completed_count"], 2)

            if duration_entries > 0:
                stats["average_duration_seconds"] = round(total_duration / duration_entries, 2)

            logger.info(f"Estadísticas calculadas para nivel {level_id}: {stats}")
            
            levels_completed = list(set(levels_completed))

            return {
                **stats,
                "progress": progress_list,
                "levels_completed": levels_completed
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")