from pathlib import Path

# Carpeta donde está este archivo (raíz del proyecto)
BASE_DIR = Path(__file__).resolve().parent

# Carpetas que la app usará
DATA_DIR = BASE_DIR / "datos"               # contactos.dat, indice.json, hash
EXPORT_DIR = BASE_DIR / "exportaciones"     # JSON y PDF exportados
RESPALDO_DIR = BASE_DIR / "respaldos"       # archivos ZIP

# Archivos principales
ARCHIVO_CONTACTOS = DATA_DIR / "contactos.dat"
ARCHIVO_INDICE = DATA_DIR / "indice.json"
ARCHIVO_HASH = DATA_DIR / "contactos.sha256"

# Codificación para todos los archivos 
ENCODING = "utf-8"

# Estructura del registro: nombre del campo -> largo en BYTES
CAMPOS = {
    "id": 8,
    "nombre": 40,
    "telefono": 15,
    "correo": 40,
    "ciudad": 24
}

# Cada registro termina con un salto de línea (1 byte)
FIN_REGISTRO = b"\n"

# Tamaño total: 8 + 40 + 15 + 40 + 24 + 1 = 128 bytes
TAM_REGISTRO = sum(CAMPOS.values()) + len(FIN_REGISTRO)
