""" Respaldo: comprime contactos.dat e indice.json en un archivo ZIP """

import zipfile
from datetime import datetime
from pathlib import Path

from nucleo.config import ARCHIVO_CONTACTOS, ARCHIVO_INDICE, ARCHIVO_HASH, RESPALDO_DIR


def crear_respaldo(destino: Path = RESPALDO_DIR) -> dict:
    """ Crea respaldo_AAAAMMDD_HHMMSS.zip y devuelve los tamaños para compararlos """
    
    archivos = [ARCHIVO_CONTACTOS, ARCHIVO_INDICE, ARCHIVO_HASH]
    faltan = [a.name for a in archivos if not a.exists()]
    if faltan:
        raise FileNotFoundError(f"No se encontró: {', '.join(faltan)}")

    destino.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_zip = destino / f"respaldo_{marca}.zip"

    with zipfile.ZipFile(ruta_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for archivo in archivos:
            z.write(archivo, arcname=archivo.name)       # sin carpetas dentro del ZIP

    # Volver a abrirlo para verificarlo y leer los tamaños de cada archivo
    with zipfile.ZipFile(ruta_zip) as z:
        detalle = [(i.filename, i.file_size, i.compress_size) for i in z.infolist()]
        danado = z.testzip()                            # None = todo se lee bien

    original = sum(tam for _, tam, _ in detalle)
    comprimido = ruta_zip.stat().st_size
    return {
        "ruta": ruta_zip,
        "detalle": detalle,
        "original": original,
        "comprimido": comprimido,
        "ahorro": 100 * (1 - comprimido / original) if original else 0.0,
        "valido": danado is None,
    }