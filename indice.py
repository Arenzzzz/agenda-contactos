""" Índice primario: relaciona cada ID con su número de registro en contactos.dat """

import json
from config import ARCHIVO_INDICE, ENCODING

class Indice:
    """ Diccionario {id: número de registro} guardado en índice.json """

    def __init__(self, ruta=ARCHIVO_INDICE):
        self.ruta = ruta
        self.mapa = {}  # ejemplo: {101: 0, 102: 1, 103:2}
        self.cargar()

    def cargar(self) -> bool:
        """ Lee indice.json. Devuelve False si no existe o está dañado """

        self.mapa = {}

        if not self.ruta.exists():
            return False
        
        try:
            with open(self.ruta, "r", encoding=ENCODING) as f:
                datos = json.load(f)
            self.mapa = {int(k): int(v) for k, v in datos.items()}
            return True
        
        except (json.JSONDecodeError, ValueError, AttributeError):
            # Contenido inválido: lo dejamos vacío para reconstruirlo
            self.mapa = {}
            return False

    def guardar(self):
        """ Escribe el índice en indice.json de forma segura """

        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.ruta.with_suffix(".tmp")

        with open(temporal, "w", encoding=ENCODING) as f:
            json.dump(self.mapa, f, indent=4, ensure_ascii=False)

        temporal.replace(self.ruta) # reemplazo en un solo paso

    def existe(self, id_contacto: int) -> bool:
        """ ¿Ya hay un contacto con este ID? """

        return id_contacto in self.mapa

    def buscar(self, id_contacto: int):
        """ Devuelve el número de registro del ID, o None si no existe """

        return self.mapa.get(id_contacto)

    def agregar(self, id_contacto: int, n_registro: int):
        """ Registra un nuevo ID y guarda el índice en disco """

        self.mapa[id_contacto] = n_registro
        self.guardar()

    def reconstruir(self, archivo):
        """ Recorre contactos.dat de forma secuencial y vuelve a armar el índice.
        Se usa si el indice.json no existe, está corrupto o no coincide con el archivo """

        self.mapa = {}

        for n, contacto in archivo.leer_todos():    # Lectura secuencial
            self.mapa[contacto.id] = n              # id -> número de registro

        self.guardar()