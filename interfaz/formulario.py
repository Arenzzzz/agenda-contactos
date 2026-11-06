""" Formulario: ficha del contacto, campos con contador de bytes y vista del registro """
from html import escape

from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout

from nucleo.config import CAMPOS, TAM_REGISTRO, ENCODING
from nucleo.registro import Contacto, RegistroError

ETIQUETAS = {"id": "ID", "nombre": "Nombre", "telefono": "Teléfono",
             "correo": "Correo", "ciudad": "Ciudad"}


class Formulario(QWidget):
    """ Agrega o edita un contacto. Avisa con señales; no escribe archivos """

    guardar_pedido = Signal()           # botón "Agregar" / "Guardar cambios"
    limpiar_pedido = Signal()           # botón "Limpiar"

    def __init__(self):
        super().__init__()
        self.tema = {}
        self.setFixedWidth(400)
        externo = QVBoxLayout(self)
        externo.setContentsMargins(12, 20, 24, 16)

        tarjeta = QFrame(objectName="tarjeta")
        caja = QVBoxLayout(tarjeta)
        caja.setContentsMargins(20, 20, 20, 20)
        caja.setSpacing(6)

        # Ficha: avatar con iniciales + título y detalle
        ficha = QHBoxLayout()
        self.avatar = QLabel("+", objectName="avatar", alignment=Qt.AlignCenter)
        self.avatar.setFixedSize(56, 56)
        ficha.addWidget(self.avatar)
        textos = QVBoxLayout()
        textos.setSpacing(2)
        self.lbl_modo = QLabel(objectName="titulo")
        self.lbl_detalle = QLabel(objectName="subtitulo")
        textos.addWidget(self.lbl_modo)
        textos.addWidget(self.lbl_detalle)
        ficha.addLayout(textos, stretch=1)
        caja.addLayout(ficha)
        self.lbl_byte = QLabel(objectName="dato")
        caja.addWidget(self.lbl_byte)
        caja.addSpacing(8)

        # Un campo por cada dato del registro, con su contador de bytes
        self.campos, self.contadores = {}, {}
        for clave in CAMPOS:
            fila = QHBoxLayout()
            fila.addWidget(QLabel(ETIQUETAS[clave]))
            fila.addStretch()
            contador = QLabel(objectName="dato")
            fila.addWidget(contador)
            caja.addLayout(fila)
            entrada = QLineEdit()
            entrada.textChanged.connect(self.actualizar_bytes)   # recalcular al escribir
            caja.addWidget(entrada)
            caja.addSpacing(2)
            self.campos[clave], self.contadores[clave] = entrada, contador
        # Solo dígitos en el ID (máximo 8, el largo del campo)
        self.campos["id"].setValidator(QRegularExpressionValidator(QRegularExpression(r"\d{0,8}")))

        # Botones
        caja.addSpacing(8)
        self.btn_guardar = QPushButton(cursor=Qt.PointingHandCursor)
        self.btn_guardar.clicked.connect(self.guardar_pedido)
        caja.addWidget(self.btn_guardar)
        btn_limpiar = QPushButton("Limpiar", objectName="secundario", cursor=Qt.PointingHandCursor)
        btn_limpiar.clicked.connect(self.limpiar_pedido)
        caja.addWidget(btn_limpiar)

        # Vista del registro tal como queda en el archivo
        caja.addSpacing(12)
        caja.addWidget(QLabel("Así se guarda en contactos.dat", objectName="subtitulo"))
        self.vista_bytes = QLabel(objectName="bytes", textFormat=Qt.RichText)
        caja.addWidget(self.vista_bytes)
        caja.addStretch()
        externo.addWidget(tarjeta)

        # ---------- Modos ----------
    def modo_nuevo(self, byte_destino: int):
        """Formulario vacío para agregar al final del archivo."""
        for entrada in self.campos.values():
            entrada.clear()
        self.campos["id"].setEnabled(True)
        self.avatar.setText("+")
        self.lbl_modo.setText("Nuevo contacto")
        self.lbl_detalle.setText("Se agregará al final del archivo")
        self.lbl_byte.setText(f"Irá en el byte {byte_destino}")
        self.btn_guardar.setText("Agregar contacto")
        self.campos["id"].setFocus()

    def mostrar_contacto(self, n: int, c: Contacto):
        """Carga un contacto existente para editarlo en el lugar."""
        for clave, entrada in self.campos.items():
            entrada.setText(str(getattr(c, clave)))
        self.campos["id"].setEnabled(False)             # el ID no se puede cambiar
        partes = c.nombre.split()
        self.avatar.setText("".join(p[0] for p in partes[:2]).upper() or "?")
        self.lbl_modo.setText("Editar contacto")
        self.lbl_detalle.setText(f"Registro {n} del archivo")
        self.lbl_byte.setText(f"Bytes {n * TAM_REGISTRO}–{(n + 1) * TAM_REGISTRO - 1} de contactos.dat")
        self.btn_guardar.setText("Guardar cambios")

    # ---------- Datos ----------
    def leer(self) -> Contacto:
        """Arma un Contacto con lo escrito. La validación completa la hace registro.py."""
        texto_id = self.campos["id"].text().strip()
        if not texto_id:
            raise RegistroError("El ID es obligatorio.")
        return Contacto(id=int(texto_id),
                        nombre=self.campos["nombre"].text(),
                        telefono=self.campos["telefono"].text(),
                        correo=self.campos["correo"].text(),
                        ciudad=self.campos["ciudad"].text())

    # ---------- Vista de bytes en vivo ----------
    def set_tema(self, tema: dict):
        self.tema = tema
        self.actualizar_bytes()

    def actualizar_bytes(self):
        """Cuántos bytes usa cada campo y cómo queda el registro de 128 bytes."""
        t = self.tema
        if not t:
            return
        lineas = []
        for clave, largo in CAMPOS.items():
            texto = self.campos[clave].text().strip()
            usados = len(texto.encode(ENCODING))            # bytes reales en UTF-8
            excede = usados > largo
            self.contadores[clave].setText(f"{usados}/{largo} bytes")
            self.contadores[clave].setStyleSheet(f"color: {t['error'] if excede else t['suave']};")
            relleno = "·" * max(0, largo - usados)           # cada punto = 1 byte de espacio
            lineas.append(
                f"<span style='color:{t['suave']}'>{clave:<9}</span>"
                f"<span style='color:{t['error'] if excede else t['texto']}'>{escape(texto[:largo])}</span>"
                f"<span style='color:{t['suave']}'>{relleno}</span>")
        lineas.append(f"<span style='color:{t['suave']}'>{'fin':<9}</span>"
                      f"<span style='color:{t['marca']}'>\\n</span>")
        self.vista_bytes.setText(
            f"<pre style='font-family:\"{t['mono']}\",monospace; font-size:11px; margin:0'>"
            + "<br>".join(lineas) + "</pre>")