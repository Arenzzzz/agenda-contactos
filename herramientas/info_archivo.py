""" Información del archivo: tamaño, fechas y permisos con os.stat() y os.access() """

import os
import stat
from datetime import datetime
from pathlib import Path

from nucleo.config import ARCHIVO_CONTACTOS, TAM_REGISTRO


def informacion(ruta: Path = ARCHIVO_CONTACTOS) -> dict:
    """ Devuelve los metadatos del archivo que guarda el sistema operativo """
    
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta.name}")

    datos = os.stat(ruta)                                  # metadatos del sistema de archivos
    formato = "%d/%m/%Y %H:%M:%S"
    return {
        "nombre": ruta.name,
        "ruta": str(ruta.resolve()),
        "tamano": datos.st_size,
        "registros": datos.st_size // TAM_REGISTRO,
        "sobrante": datos.st_size % TAM_REGISTRO,         # debe ser 0 en un archivo sano
        "modificado": datetime.fromtimestamp(datos.st_mtime).strftime(formato),
        "accedido": datetime.fromtimestamp(datos.st_atime).strftime(formato),
        "permisos": stat.filemode(datos.st_mode),          # ejemplo: -rw-r--r--
        "octal": oct(datos.st_mode & 0o777),               # ejemplo: 0o644
        "lectura": os.access(ruta, os.R_OK),
        "escritura": os.access(ruta, os.W_OK),
    }