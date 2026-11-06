""" Integridad de contactos.dat con SHA-256 """

import hashlib

from nucleo.config import ARCHIVO_CONTACTOS, ARCHIVO_HASH, ENCODING

def calcular_hash(ruta=ARCHIVO_CONTACTOS) -> str:
    """ Calcula el SHA-256 del archivo leyéndolo por bloques """

    sha = hashlib.sha256()

    with open(ruta, "rb") as f:
        while bloque := f.read(4096):   # leer de 4 KB en 4KB
            sha.update(bloque)          # ir alimentando el hash

        return sha.hexdigest()          # 64 caracteres hexadecimales

def guardar_hash(ruta=ARCHIVO_CONTACTOS, ruta_hash=ARCHIVO_HASH) -> str:
    """ Calcula el hash actual y lo guarda en contactos.sha256 """

    valor = calcular_hash(ruta)
    temporal = ruta_hash.with_suffix(".tmp")    # escritura segura

    with open(temporal, "w", encoding=ENCODING) as f:
        f.write(valor)

    temporal.replace(ruta_hash)

    return valor

def verificar(ruta=ARCHIVO_CONTACTOS, ruta_hash=ARCHIVO_HASH) -> tuple[str, str, str]:
    """ Compara el hash guardado con el actual. 
        Devuelve (estado, hash_guardado, hash_actual) 
        estado: 'ok', 'alterado' o 'sin_hash' """

    actual = calcular_hash(ruta)

    if not ruta_hash.exists():
        return "sin_hash", "", actual

    with open(ruta_hash, "r", encoding=ENCODING) as f:
        guardado = f.read().strip()

        if guardado == actual:
            return "ok", guardado, actual   

        return "alterado", guardado, actual