"""Módulo de registro de eventos y errores (único uso permitido de archivos)."""

import logging
import os

# Ruta absoluta de la carpeta logs, relativa a la ubicación de este archivo
RUTA_LOGS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
# Archivo donde se registran todos los eventos y errores
ARCHIVO_LOG = os.path.join(RUTA_LOGS, "software_fj.log")


def obtener_logger() -> logging.Logger:
    """Devuelve el logger único del sistema, configurándolo la primera vez."""
    logger = logging.getLogger("SoftwareFJ")
    # Evita duplicar manejadores si la función se llama varias veces
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    try:
        # Crea la carpeta de logs si no existe
        os.makedirs(RUTA_LOGS, exist_ok=True)
        # Manejador de archivo con codificación UTF-8
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    except OSError:
        # Si el archivo no se puede abrir, se usa la consola para no detener el sistema
        manejador = logging.StreamHandler()
    # Formato: fecha, nivel y mensaje
    manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    logger.addHandler(manejador)
    return logger


# Instancia compartida que importan los demás módulos
log = obtener_logger()
