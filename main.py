""" Punto de entrada: python3 main.py """

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from interfaz.ventana import VentanaPrincipal
from nucleo.agenda import Agenda
from nucleo.registro import RegistroError


def iniciar_agenda():
    """ Abre archivo, índice e integridad. Si algo grave falla, avisa y devuelve None """

    try:
        return Agenda()
    except RegistroError as e:
        QMessageBox.critical(None, "Archivo corrupto",
                             f">> No se puede abrir contactos.dat:\n\n{e}\n\n"
                             "Restaura un respaldo ZIP para continuar.")
    except PermissionError:
        QMessageBox.critical(None, "Sin permisos",
                             ">> No hay permisos para leer o escribir los archivos de datos.")
    except OSError as e:
        QMessageBox.critical(None, "Error de archivo", f">> No se pudo acceder a los datos:\n\n{e}")
    return None


def main():
    app = QApplication(sys.argv)
    agenda = iniciar_agenda()
    if agenda is None:
        sys.exit(1)
    ventana = VentanaPrincipal(agenda, tema="Bytes")
    ventana.show()
    QTimer.singleShot(300, ventana.avisos_iniciales)   # avisos con la ventana ya visible
    sys.exit(app.exec())


if __name__ == "__main__":
    main()