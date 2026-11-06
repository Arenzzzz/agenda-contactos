""" Barra lateral: nombre de la app y accesos rápidos """

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from nucleo.config import TAM_REGISTRO


class BarraLateral(QFrame):
    """ Recibe las secciones como {título: [(texto, función), ...]} y arma los botones """

    def __init__(self, secciones: dict):
        super().__init__(objectName="lateral")      # el QSS la pinta con "#lateral"
        self.setFixedWidth(220)
        caja = QVBoxLayout(self)
        caja.setContentsMargins(14, 20, 14, 20)
        caja.setSpacing(2)

        caja.addWidget(QLabel("Agenda", objectName="logo"))
        caja.addWidget(QLabel(f"Registros fijos de {TAM_REGISTRO} bytes", objectName="subtitulo"))

        for titulo, botones in secciones.items():
            caja.addWidget(QLabel(titulo, objectName="seccion"))
            for texto, funcion in botones:
                boton = QPushButton(texto)
                boton.setCursor(Qt.PointingHandCursor)   # manita al pasar el mouse
                boton.clicked.connect(funcion)           # al hacer clic, llamar a la función
                caja.addWidget(boton)

        caja.addStretch()                       # empuja todo hacia arriba