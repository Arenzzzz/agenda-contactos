""" Agenda: coordina el archivo de contactos y el índice primario """

from almacenamiento import ArchivoContactos
from indice import Indice
from registro import Contacto, RegistroError


class Agenda:
    """ Punto de entrada para la interfaz: agregar, buscar, modificar, listar """

    def __init__(self):
        self.archivo = ArchivoContactos()
        self.indice = Indice()                     # intenta cargar indice.json
        self.indice_reconstruido = False
        self._verificar_indice()

    def _verificar_indice(self):
        """Si el índice no coincide con el archivo, lo reconstruye."""
        total = self.archivo.cantidad_registros()
        if len(self.indice.mapa) != total:
            self.indice.reconstruir(self.archivo)
            self.indice_reconstruido = True        # la interfaz avisará al usuario

    def agregar(self, contacto: Contacto):
        """ Agrega un contacto nuevo. Devuelve su número de registro """

        if self.indice.existe(contacto.id):
            raise RegistroError(f">> Ya existe un contacto con el ID {contacto.id}")

        n = self.archivo.agregar(contacto)      # 1. Escribir al final del .dat
        self.indice.agregar(contacto.id, n)     # 2. Registrar id -> n en el índice 

        return n

    def buscar(self, id_contacto: int) -> tuple[int, Contacto]:
        """ Busca por ID: índice -> número de registro -> seek() -> leer """

        n = self.indice.buscar(id_contacto)     # 1. Consultar el índice

        if n is None:
            raise KeyError(f">> No existe un contacto con el ID {id_contacto}")

        contacto = self.archivo.leer(n)         # 2. Acceso directo con seek()

        return n, contacto

    def modificar(self, id_contacto: int, nuevos: Contacto) -> int:
        """ Modifica un contacto en el lugar. El ID no se puede cambiar """

        n, _ = self.buscar(id_contacto)         # índice -> registro (o KeyError)

        if nuevos.id != id_contacto:
            raise RegistroError(">> No se puede cambiar el ID de un contacto")

        self.archivo.sobrescribir(n, nuevos)    # seek() + write de 128 bytes

        return n

    def listar(self) -> list[Contacto]:
        """ Todos los contactos, en orden de registro (lectura secuencial) """

        return [c for _, c in self.archivo.leer_todos()]
    