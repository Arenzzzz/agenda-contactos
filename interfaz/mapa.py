""" Mapa del archivo: dibuja contactos.dat como bloques de tamaño fijo y marca el puntero """

from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QFont, QPolygonF, QPen
from PySide6.QtWidgets import QWidget, QToolTip

from nucleo.config import TAM_REGISTRO


class MapaArchivo(QWidget):
    """ Cada rectángulo es un registro de 128 bytes; el resaltado es donde está tell().
        Al pasar el mouse muestra el contacto y al hacer clic avisa qué registro se eligió """

    registro_elegido = Signal(int)          # señal: "el usuario hizo clic en el registro n"

    def __init__(self):
        super().__init__()
        self.total = 0                       # cantidad de registros del archivo
        self.actual = None                   # registro seleccionado (o None)
        self.etiquetas = []                  # "ID 101 · Ana López" por registro
        self.colores = {}                    # tema activo
        self.rects = []                      # rectángulo dibujado de cada registro
        self.sobre = None                    # registro bajo el mouse
        self.x_puntero = None                # posición (x) de la flecha
        self.nuevo = False                   # mostrar el hueco del próximo registro
        self.setFixedHeight(92)
        self.setMouseTracking(True)          # recibir movimiento del mouse sin hacer clic

        # Animación de la flecha: se desliza de un registro a otro
        self.animacion = QVariantAnimation(self, duration=280, easingCurve=QEasingCurve.OutCubic)
        self.animacion.valueChanged.connect(self._mover_puntero)

    def set_tema(self, tema: dict):
        self.colores = tema
        self.update()                        # pedir a Qt que vuelva a dibujar

    def set_datos(self, total: int, actual=None, etiquetas=None):
        self.total = total
        if etiquetas is not None:
            self.etiquetas = etiquetas
        anterior, self.actual = self.actual, actual
        self._calcular_rects()
        if actual is not None and actual < len(self.rects):
            destino = self.rects[actual].center().x()
            # Si ya había flecha, sale desde donde estaba; si no, aparece directo
            inicio = self.x_puntero if (anterior is not None and self.x_puntero is not None) else destino
            self.animacion.stop()
            self.animacion.setStartValue(float(inicio))
            self.animacion.setEndValue(float(destino))
            self.animacion.start()
        else:
            self.x_puntero = None
        self.update()

    def set_nuevo(self, activo: bool):
        """ Muestra u oculta el hueco donde caerá el próximo registro """
        self.nuevo = activo
        self._calcular_rects()
        self.update()

    def _mover_puntero(self, x):
        self.x_puntero = x
        self.update()

    def _calcular_rects(self):
        """ Calcula dónde va cada bloque según el ancho disponible """

        self.rects = []
        self.ancho_bloque = 64.0
        espacios = self.total + (1 if self.nuevo else 0)   # +1 para el hueco del nuevo
        if espacios == 0:
            return
        separacion, y, alto = 4, 22.0, 34.0
        bloque = max(8.0, min(64.0, (self.width() - separacion * (espacios - 1)) / espacios))
        self.ancho_bloque = bloque
        visibles = min(self.total, int((self.width() + separacion) // (bloque + separacion)))
        for n in range(visibles):
            self.rects.append(QRectF(n * (bloque + separacion), y, bloque, alto))

    def resizeEvent(self, evento):
        """ Si la ventana cambia de tamaño, recalcular los bloques """
        self._calcular_rects()
        if self.actual is not None and self.actual < len(self.rects):
            self.x_puntero = self.rects[self.actual].center().x()
        super().resizeEvent(evento)

    # ---------- Interacción con el mouse ----------
    def _registro_en(self, punto):
        """ ¿Qué registro está bajo este punto? (o None) """
        
        for n, rect in enumerate(self.rects):
            if rect.contains(punto):
                return n
        return None

    def mouseMoveEvent(self, evento):
        """ Al mover el mouse: resaltar el bloque y mostrar a quién pertenece """
        
        n = self._registro_en(evento.position())
        if n != self.sobre:
            self.sobre = n
            self.setCursor(Qt.PointingHandCursor if n is not None else Qt.ArrowCursor)
            self.update()
        if n is not None:
            nombre = self.etiquetas[n] if n < len(self.etiquetas) else ""
            QToolTip.showText(evento.globalPosition().toPoint(),
                              f"Registro {n}  ·  bytes {n * TAM_REGISTRO}–{(n + 1) * TAM_REGISTRO - 1}\n{nombre}",
                              self)

    def leaveEvent(self, _evento):
        """ El mouse salió del mapa: quitar el resaltado """

        self.sobre = None
        self.update()

    def mousePressEvent(self, evento):
        """ Clic en un bloque: avisar qué registro se eligió """

        n = self._registro_en(evento.position())
        if n is not None:
            self.registro_elegido.emit(n)

    # ---------- Dibujo ----------
    def paintEvent(self, _evento):
        if not self.colores:
            return
        c = self.colores
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)   # bordes suaves

        # Encabezado: nombre y tamaño del archivo
        p.setPen(QColor(c["suave"]))
        p.setFont(QFont(c["mono"], 10))
        p.drawText(0, 12, f"contactos.dat     {self.total * TAM_REGISTRO} bytes     "
                          f"{self.total} registros de {TAM_REGISTRO} bytes     clic en un bloque para abrirlo")

        if self.total == 0 and not self.nuevo:
            p.drawText(0, 44, "Archivo vacío: agrega el primer contacto.")
            p.end()
            return

        # Un rectángulo por registro
        for n, rect in enumerate(self.rects):
            es_actual = n == self.actual
            color = QColor(c["marca"] if es_actual else (c["acento"] if n == self.sobre else c["borde"]))
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(rect, 3, 3)
            if rect.width() >= 26:                       # número de registro si cabe
                resaltado = es_actual or n == self.sobre
                p.setPen(QColor("#FFFFFF" if es_actual else (c["sobre_acento"] if resaltado else c["suave"])))
                p.setFont(QFont(c["mono"], 9, QFont.Bold if resaltado else QFont.Normal))
                p.drawText(rect, Qt.AlignCenter, str(n))

        # Hueco punteado: aquí caerá el nuevo registro (seek al final)
        if self.nuevo and len(self.rects) == self.total:
            x = self.total * (self.ancho_bloque + 4)
            hueco = QRectF(x, 22, self.ancho_bloque, 34)
            p.setPen(QPen(QColor(c["marca"]), 1.5, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(hueco.adjusted(1, 1, -1, -1), 3, 3)
            p.setFont(QFont(c["mono"], 9, QFont.Bold))
            p.drawText(hueco, Qt.AlignCenter, str(self.total))
            p.setPen(QColor(c["texto"]))
            p.setFont(QFont(c["mono"], 10, QFont.Bold))
            centro = hueco.center().x()
            p.drawText(QRectF(min(max(0, centro - 70), self.width() - 140), 72, 140, 18),
                       Qt.AlignCenter, f"nuevo en byte {self.total * TAM_REGISTRO}")

        # Hay más registros de los que caben
        if len(self.rects) < self.total:
            p.setPen(QColor(c["suave"]))
            p.drawText(QRectF(self.width() - 40, 22, 40, 34), Qt.AlignCenter, "…")

        # Flecha y posición del puntero
        if self.x_puntero is not None and self.actual is not None:
            x, y = self.x_puntero, 22 + 34
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(c["marca"]))
            p.drawPolygon(QPolygonF([QPointF(x, y + 4), QPointF(x - 6, y + 12), QPointF(x + 6, y + 12)]))
            p.setPen(QColor(c["texto"]))
            p.setFont(QFont(c["mono"], 10, QFont.Bold))
            x_texto = min(max(0, x - 60), self.width() - 120)
            p.drawText(QRectF(x_texto, y + 14, 120, 18), Qt.AlignCenter,
                       f"tell() = {self.actual * TAM_REGISTRO}")