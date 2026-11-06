""" Panel central: búsqueda por ID, mapa del archivo y tabla de contactos """

from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QHBoxLayout, QVBoxLayout,
)

from interfaz.mapa import MapaArchivo
from nucleo.config import TAM_REGISTRO

COLUMNAS = ("Reg.", "Byte", "ID", "Nombre", "Teléfono", "Correo", "Ciudad")
COL_ID = 2


class PanelContactos(QWidget):
    """ Muestra los contactos. No toca archivos: solo avisa qué eligió el usuario """

    contacto_elegido = Signal(int)      # clic en una fila  -> ID
    registro_elegido = Signal(int)      # clic en el mapa   -> número de registro
    busqueda_pedida = Signal(int)       # Enter o "Buscar"  -> ID (-1 si está vacío)

    def __init__(self):
        super().__init__()
        self.tema = {}
        caja = QVBoxLayout(self)
        caja.setContentsMargins(24, 20, 12, 16)
        caja.setSpacing(12)

        # Encabezado: título a la izquierda, total a la derecha
        encabezado = QHBoxLayout()
        encabezado.addWidget(QLabel("Contactos", objectName="titulo"))
        encabezado.addStretch()
        self.lbl_total = QLabel(objectName="subtitulo")
        encabezado.addWidget(self.lbl_total)
        caja.addLayout(encabezado)

        # Búsqueda por ID (solo dígitos, máximo 8)
        busqueda = QHBoxLayout()
        self.entrada_buscar = QLineEdit(placeholderText="Buscar por ID  (índice → seek → read)")
        self.entrada_buscar.setValidator(QRegularExpressionValidator(QRegularExpression(r"\d{0,8}")))
        self.entrada_buscar.returnPressed.connect(self._pedir_busqueda)
        boton = QPushButton("Buscar", cursor=Qt.PointingHandCursor)
        boton.clicked.connect(self._pedir_busqueda)
        busqueda.addWidget(self.entrada_buscar)
        busqueda.addWidget(boton)
        caja.addLayout(busqueda)

        # Mapa del archivo dentro de una tarjeta
        tarjeta_mapa = QFrame(objectName="tarjeta")
        caja_mapa = QVBoxLayout(tarjeta_mapa)
        caja_mapa.setContentsMargins(16, 12, 16, 8)
        self.mapa = MapaArchivo()
        self.mapa.registro_elegido.connect(self.registro_elegido)   # reenviar la señal
        caja_mapa.addWidget(self.mapa)
        caja.addWidget(tarjeta_mapa)

        # Tabla
        self.tabla = QTableWidget(0, len(COLUMNAS))
        self.tabla.setHorizontalHeaderLabels(COLUMNAS)
        self.tabla.verticalHeader().setVisible(False)                  # sin números de fila de Qt
        self.tabla.verticalHeader().setDefaultSectionSize(34)          # alto de cada fila
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)  # seleccionar filas completas
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)   # se edita en el formulario
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.setSortingEnabled(True)                             # clic en encabezado = ordenar
        self.tabla.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
        cabecera = self.tabla.horizontalHeader()
        cabecera.setSectionResizeMode(QHeaderView.ResizeToContents)   # cada columna mide lo que su texto
        cabecera.setStretchLastSection(True)                          # la última ocupa el sobrante
        self.tabla.itemSelectionChanged.connect(self._fila_elegida)

        marco = QFrame(objectName="tarjeta")
        caja_marco = QVBoxLayout(marco)
        caja_marco.setContentsMargins(1, 1, 1, 1)
        caja_marco.addWidget(self.tabla)
        caja.addWidget(marco, stretch=1)          # la tabla ocupa el espacio sobrante

    # ---------- Datos ----------
    def set_tema(self, tema: dict):
        self.tema = tema
        self.mapa.set_tema(tema)

    def cargar(self, registros: list):
        """registros = [(n, contacto), ...] en el orden del archivo."""
        self.tabla.setSortingEnabled(False)          # no reordenar mientras llenamos
        self.tabla.setRowCount(0)                    # vaciar la tabla
        for n, c in registros:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            valores = (n, n * TAM_REGISTRO, c.id, c.nombre, c.telefono, c.correo, c.ciudad)
            for col, valor in enumerate(valores):
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, valor)   # los números se ordenan como números
                if col < 2 and self.tema:             # Reg. y Byte en monoespaciada
                    item.setFont(QFont(self.tema["mono"], 11))
                if isinstance(valor, int):
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, col, item)
        self.tabla.setSortingEnabled(True)

        total = len(registros)
        self.lbl_total.setText(f"{total} contacto{'s' if total != 1 else ''}")
        etiquetas = [f"ID {c.id}  ·  {c.nombre}" for _, c in registros]
        self.mapa.set_datos(total, self.mapa.actual, etiquetas)

    def seleccionar_id(self, id_contacto: int):
        """Marca la fila del ID sin volver a disparar la señal."""
        for fila in range(self.tabla.rowCount()):
            if self.tabla.item(fila, COL_ID).data(Qt.DisplayRole) == id_contacto:
                self.tabla.blockSignals(True)
                self.tabla.selectRow(fila)
                self.tabla.blockSignals(False)
                self.tabla.scrollToItem(self.tabla.item(fila, 0))
                return

    def limpiar_seleccion(self):
        self.tabla.blockSignals(True)
        self.tabla.clearSelection()
        self.tabla.blockSignals(False)

    def enfocar_busqueda(self):
        """Para el atajo Cmd+F: poner el cursor en la búsqueda."""
        self.entrada_buscar.setFocus()
        self.entrada_buscar.selectAll()

    # ---------- Señales internas ----------
    def _fila_elegida(self):
        filas = self.tabla.selectionModel().selectedRows()
        if filas:
            id_contacto = self.tabla.item(filas[0].row(), COL_ID).data(Qt.DisplayRole)
            self.contacto_elegido.emit(id_contacto)

    def _pedir_busqueda(self):
        texto = self.entrada_buscar.text().strip()
        self.busqueda_pedida.emit(int(texto) if texto else -1)