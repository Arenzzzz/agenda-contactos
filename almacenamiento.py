import os

from config import ARCHIVO_CONTACTOS, TAM_REGISTRO
from registro import Contacto, empaquetar, desempaquetar, RegistroError

class ArchivoContactos:
    """ Maneja el archivo de registros de tamaño fijo """

    def __init__(self, ruta=ARCHIVO_CONTACTOS):
        self.ruta = ruta
        self.utlima_posicion = 0    # último valor de tell();
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        """ Crea la carpeta y el archivo vacío si todavía no existen """

        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta.exists():
            self.ruta.touch()   # Crea el archivo vacío

    def cantidad_registros(self) -> int:
        """ Tamaño del archivo / tamaño del registro = número de registros """

        tamanio = os.path.getsize(self.ruta)

        # Si no es múltiplo de 128, hay un registro incompleto: archivo dañado
        if tamanio % TAM_REGISTRO != 0:
            raise RegistroError(
                f">> El archivo mide {tamanio} bytes, que no es múltiplo de {TAM_REGISTRO}"
            )

        return tamanio // TAM_REGISTRO

    @staticmethod
    def posicion(n: int) -> int:
        """ Byte donde empieza el registro n (numerado desde 0) """

        return n * TAM_REGISTRO

    def agregar(self, contacto: Contacto) -> int:
        """ Escribe el contacto al final y devuelve su número de registro """

        registro = empaquetar(contacto)                 # valudar y convertir a 128 bytes

        with open(self.ruta, "r+b") as f:               
            f.seek(0, os.SEEK_END)                      # mover el puntero al final
            self.ultima_posicion = f.tell()             # ¿en qué byte quedamos?
            f.write(registro)                           # escribir los 128 bytes

        return self.ultima_posicion // TAM_REGISTRO     # byte / 128 = número de registro

    def leer(self, n: int) -> Contacto:
        """ Lee SOLO el registro n, sin recorrer los anteriores """

        if n < 0 or n >= self.cantidad_registros():
            raise IndexError(f">> El registro {n} no existe.")

        with open(self.ruta, "rb") as f:
            f.seek(self.posicion(n))            # saltar directo al registro
            self.ultima_posicion = f.tell()     # confirmar la posición
            datos = f.read(TAM_REGISTRO)        # leer exactamente 128 bytes

        return desempaquetar(datos)

    def sobrescribir(self, n: int, contacto: Contacto) -> None:
        """ Modificación en el lugar: reemplaza solo los 128 bytes del registro n """

        if n < 0 or n >= self.cantidad_registros():
            raise IndexError(f">> El registro {n} no existe.")

        registro = empaquetar(contacto)     # validar y convertir a bytes

        with open(self.ruta, "r+b") as f:
            f.seek(self.posicion(n))        # se para al incio del registro
            self.ultima_posicion = f.tell()
            f.write(registro)               # escribir encima, solo 128 bytes

    def leer_todos(self):
        """ Lectura SECUENCIAL: devuelve (n, contacto) uno por uno,
        Se usa para mostrar la tabla, exportar y reconstruir el índice """

        total = self.cantidad_registros()

        with open(self.ruta, "rb") as f:
            for n in range(total):
                datos = f.read(TAM_REGISTRO)    # el puntero avanza 128 bytes solo
                yield n, desempaquetar(datos)

                