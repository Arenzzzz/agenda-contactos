from dataclasses import dataclass, asdict
from nucleo.config import CAMPOS, TAM_REGISTRO, FIN_REGISTRO, ENCODING

class RegistroError(ValueError):
    """ Error de validación o registro corrupto """

@dataclass
class Contacto:
    id: int
    nombre: str
    telefono: str
    correo: str
    ciudad: str

    def a_dict(self) -> dict:
        # Convierte el contacto en diccionario (se usará para exportar a JSON)
        return asdict(self)

def validar(c: Contacto) -> None:

    # Revisa que los datos tengan sentido antes de guardarlos
    if not isinstance(c.id, int) or c.id <= 0:
        raise RegistroError(">> El ID debe ser un número entero positivo.")
    if not c.nombre.strip():
        raise RegistroError(">> El nombre es obligatorio.")
    if c.correo.strip() and "@" not in c.correo:
        raise RegistroError(">> El correo no es válido.")

def _campo_a_bytes(nombre: str, valor, largo: int) -> bytes: # - FUNCIÓN AUXILIAR -
    """ Codifica un campo en UTF-8 y lo rellena con espacios hasta su largo """

    datos = str(valor).strip().encode(ENCODING)    # texto -> bytes

    if len(datos) > largo:  # medimos en BYTES, no en letras
        raise RegistroError(
            f">> El campo '{nombre}' ocupa {len(datos)} bytes y el máximo es {largo}."
        )

    return datos.ljust(largo, b" ")

def empaquetar(c: Contacto) -> bytes:
    """ Contacto -> bytes de tamaño fijo (128) """

    validar(c)                                              # 1. revisar los datos
    partes = [
        _campo_a_bytes(nombre, getattr(c, nombre), largo)
        for nombre, largo in CAMPOS.items()                 # 2. cada campo, en orden
    ]
    registro = b"".join(partes) + FIN_REGISTRO              # 3. unir todo con + "\n"
    assert len(registro) == TAM_REGISTRO                    # 4. seguridad: deben ser 128

    return registro

def desempaquetar(datos: bytes) -> Contacto:
    """ Bytes de tamaño fijo (128) -> Contacto """

    # 1. ¿El registro está completo?
    if len(datos) != TAM_REGISTRO or not datos.endswith(FIN_REGISTRO):
        raise RegistroError(">> Registro incompleto o corrupto.")

    valores, pos = {}, 0
    try:

        # 2. Cortar cada campo según su largo
        for nombre, largo in CAMPOS.items():
            campo = datos[pos: pos + largo] # rebanada de bytes
            valores[nombre] = campo.decode(ENCODING).rstrip()   #bytes -> texto sin relleno
            pos += largo    # avanzar al siguiente campo

        # 3. El ID vuelve a ser número
        valores['id'] = int(valores["id"])

    except (UnicodeDecodeError, ValueError) as e:
        raise RegistroError(f">> Registro corrupto: {e}") from e

    return Contacto(**valores)