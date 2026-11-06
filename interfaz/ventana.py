""" Ventana principal: une los paneles, el menú, la barra de estado y la Agenda """

from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, QMessageBox, QStatusBar,
)

from interfaz.barra_lateral import BarraLateral
from interfaz.estilos import TEMAS, construir_qss
from interfaz.formulario import Formulario
from interfaz.panel_contactos import PanelContactos
from nucleo.agenda import Agenda
from nucleo.config import TAM_REGISTRO
from nucleo.integridad import verificar
from nucleo.registro import RegistroError

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from herramientas.exportar import exportar_json, exportar_pdf
from herramientas.respaldo import crear_respaldo
from herramientas.info_archivo import informacion

class VentanaPrincipal(QMainWindow):
    """ Es el único componente que habla con la Agenda (los archivos) """

    def __init__(self, agenda: Agenda, tema: str = "Bytes"):
        super().__init__()
        self.agenda = agenda
        self.tema = TEMAS[tema]
        self.id_editando = None                  # None = modo "nuevo contacto"

        self.setWindowTitle("Agenda de Contactos · Acceso aleatorio")
        self.resize(1320, 800)
        self.setMinimumSize(1100, 650)

        # Componentes
        self.lateral = BarraLateral({
            "Contactos": [("➕   Nuevo contacto", self.nuevo_contacto),
                          ("🔄   Recargar lista", self.recargar)],
            "Herramientas": [("📄   Exportar JSON", self.accion_exportar_json),
                             ("🧾   Exportar PDF", self.accion_exportar_pdf),
                             ("🗜️   Respaldo ZIP", self.accion_respaldo),
                             ("ℹ️   Info del archivo", self.accion_info_archivo),
                             ("🛡️   Verificar integridad", self.verificar_integridad)],
        })
        self.panel = PanelContactos()
        self.formulario = Formulario()

        # Conexiones: qué hace la ventana cuando un componente avisa algo
        self.panel.contacto_elegido.connect(self.abrir_contacto)
        self.panel.registro_elegido.connect(self.abrir_registro)
        self.panel.busqueda_pedida.connect(self.buscar_por_id)
        self.formulario.guardar_pedido.connect(self.guardar)
        self.formulario.limpiar_pedido.connect(self.nuevo_contacto)

        # Distribución: [lateral | panel | formulario]
        central = QWidget()
        fila = QHBoxLayout(central)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(0)
        fila.addWidget(self.lateral)
        fila.addWidget(self.panel, stretch=1)   # el panel crece con la ventana
        fila.addWidget(self.formulario)
        self.setCentralWidget(central)

        self._crear_menu(tema)
        self._crear_barra_estado()
        self.aplicar_tema(tema)
        self.nuevo_contacto()                   # arrancar con el formulario listo para agregar

        # ================= Menú y barra de estado =================
    def _crear_menu(self, tema_inicial: str):
        menu = self.menuBar()

        archivo = menu.addMenu("&Archivo")
        self._accion(archivo, "Exportar a JSON…", self.accion_exportar_json)
        self._accion(archivo, "Exportar reporte PDF…", self.accion_exportar_pdf)
        archivo.addSeparator()
        self._accion(archivo, "Crear respaldo ZIP", self.accion_respaldo)
        archivo.addSeparator()
        self._accion(archivo, "Salir", self.close, QKeySequence.Quit)

        contactos = menu.addMenu("&Contactos")
        self._accion(contactos, "Nuevo contacto", self.nuevo_contacto, QKeySequence.New)
        self._accion(contactos, "Buscar por ID", self.panel.enfocar_busqueda, QKeySequence.Find)
        self._accion(contactos, "Recargar lista", self.recargar, QKeySequence.Refresh)

        herramientas = menu.addMenu("&Herramientas")
        self._accion(herramientas, "Verificar integridad (SHA-256)", self.verificar_integridad)
        self._accion(herramientas, "Información del archivo", self.accion_info_archivo)

        ver = menu.addMenu("&Ver")
        grupo = QActionGroup(self)               # solo un tema marcado a la vez
        for nombre in TEMAS:
            accion = QAction(f"Tema {nombre}", self, checkable=True)
            accion.setChecked(nombre == tema_inicial)
            accion.triggered.connect(lambda _=False, n=nombre: self.aplicar_tema(n))
            grupo.addAction(accion)
            ver.addAction(accion)

        ayuda = menu.addMenu("A&yuda")
        self._accion(ayuda, "Acerca de", self.acerca_de)

    def _accion(self, menu, texto, funcion, atajo=None):
        """ Crea una opción de menú con su función y, si se indica, su atajo de teclado """
        accion = QAction(texto, self)
        if atajo is not None:
            accion.setShortcut(atajo)
        accion.triggered.connect(funcion)
        menu.addAction(accion)

    def _crear_barra_estado(self):
        barra = QStatusBar()
        self.setStatusBar(barra)
        self.lbl_posicion = QLabel()             # seek()/tell() a la izquierda
        self.lbl_integridad = QLabel()           # estado SHA-256 a la derecha
        barra.addWidget(self.lbl_posicion, 1)
        barra.addPermanentWidget(self.lbl_integridad)

    def mostrar_posicion(self, n: int):
        """ Cálculo de seek() y valor REAL de tell() en la barra de estado y el mapa """

        tell = self.agenda.archivo.ultima_posicion
        self.lbl_posicion.setText(
            f"Registro {n}     seek({n} × {TAM_REGISTRO}) → byte {n * TAM_REGISTRO}     tell() = {tell}")
        self.panel.mapa.set_nuevo(False)
        self.panel.mapa.set_datos(self.agenda.archivo.cantidad_registros(), n)

    def actualizar_integridad(self):
        alterado = self.agenda.integridad[0] == "alterado"
        self.lbl_integridad.setText("●  Archivo alterado" if alterado else "●  Integridad OK")
        color = self.tema["error"] if alterado else self.tema["ok"]
        self.lbl_integridad.setStyleSheet(f"color: {color}; font-weight: bold;")

        # ================= Contactos =================
    def recargar(self):
        """ Lectura secuencial del archivo para llenar la tabla y el mapa """

        try:
            self.panel.cargar(list(self.agenda.archivo.leer_todos()))
        except RegistroError as e:
            QMessageBox.critical(self, "Archivo corrupto", str(e))

    def abrir_contacto(self, id_contacto: int):
        """ Buscar por ID: índice -> seek -> read, y mostrarlo en el formulario """

        n, c = self.agenda.buscar(id_contacto)
        self.id_editando = c.id
        self.formulario.mostrar_contacto(n, c)
        self.panel.seleccionar_id(c.id)
        self.mostrar_posicion(n)

    def abrir_registro(self, n: int):
        """ Clic en un bloque del mapa: leer ese registro directo con seek() """

        self.abrir_contacto(self.agenda.archivo.leer(n).id)

    def buscar_por_id(self, id_contacto: int):
        if id_contacto < 0:
            QMessageBox.information(self, "Búsqueda", "Escribe un ID para buscar.")
            return
        try:
            self.abrir_contacto(id_contacto)
        except KeyError as e:
            QMessageBox.warning(self, "No encontrado", str(e).strip("'\""))

    def nuevo_contacto(self):
        """ Formulario vacío y hueco punteado al final del archivo """

        self.id_editando = None
        total = self.agenda.archivo.cantidad_registros()
        self.formulario.modo_nuevo(total * TAM_REGISTRO)
        self.panel.limpiar_seleccion()
        self.panel.mapa.set_datos(total, None)
        self.panel.mapa.set_nuevo(True)
        self.lbl_posicion.setText(f"Nuevo registro     seek(0, SEEK_END) → byte {total * TAM_REGISTRO}")

    def guardar(self):
        """ Agrega o modifica según el modo del formulario """

        try:
            contacto = self.formulario.leer()
            if self.id_editando is None:
                n = self.agenda.agregar(contacto)
                mensaje = f"Contacto agregado en el registro {n}."
            else:
                n = self.agenda.modificar(self.id_editando, contacto)
                mensaje = f"Registro {n} modificado en el lugar."
        except (RegistroError, KeyError) as e:
            QMessageBox.warning(self, "No se pudo guardar", str(e).strip("'\""))
            return
        except PermissionError:
            QMessageBox.critical(self, "Sin permisos", "No hay permiso para escribir en contactos.dat.")
            return

        self.recargar()
        self.abrir_contacto(contacto.id)
        self.actualizar_integridad()
        self.statusBar().showMessage(mensaje, 4000)    # mensaje temporal de 4 segundos

        # ================= Herramientas =================
    def accion_exportar_json(self):
        try:
            ruta = exportar_json(self.agenda)
        except (OSError, RegistroError) as e:
            QMessageBox.critical(self, "No se pudo exportar", str(e))
            return
        total = self.agenda.archivo.cantidad_registros()
        QMessageBox.information(self, "JSON exportado",
                                f"Se exportaron {total} contactos a:\n{ruta}")

    def accion_exportar_pdf(self):
        try:
            ruta_json = exportar_json(self.agenda)     # JSON al día antes del reporte
            ruta_pdf = exportar_pdf(ruta_json)
        except (OSError, RegistroError) as e:
            QMessageBox.critical(self, "No se pudo generar el PDF", str(e))
            return
        self.statusBar().showMessage(f"Reporte generado: {ruta_pdf}", 5000)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(ruta_pdf)))   # abrir el PDF

    def accion_respaldo(self):
        try:
            r = crear_respaldo()
        except OSError as e:                       # incluye FileNotFoundError
            QMessageBox.critical(self, "No se pudo crear el respaldo", str(e))
            return

        filas = "".join(
            f"<tr><td>{nombre}</td><td align='right'>{orig:,} B</td>"
            f"<td align='right'>{comp:,} B</td></tr>"
            for nombre, orig, comp in r["detalle"])
        estado = ("✔ Verificado: el ZIP se lee completo (CRC correcto)" if r["valido"]
                  else "✖ El ZIP no pasó la verificación")
        QMessageBox.information(
            self, "Respaldo creado",
            f"<b>{r['ruta'].name}</b><br><br>"
            "<table cellpadding='4'>"
            "<tr><th align='left'>Archivo</th><th>Original</th><th>Comprimido</th></tr>"
            f"{filas}"
            f"<tr><td><b>ZIP completo</b></td><td align='right'><b>{r['original']:,} B</b></td>"
            f"<td align='right'><b>{r['comprimido']:,} B</b></td></tr>"
            "</table><br>"
            f"Ahorro: <b>{r['ahorro']:.1f}%</b><br>{estado}")

    def accion_info_archivo(self):
        try:
            i = informacion()
        except OSError as e:
            QMessageBox.critical(self, "No se pudo leer la información", str(e))
            return

        si_no = lambda valor: "✔ Sí" if valor else "✖ No"
        estructura = ("Correcta (múltiplo exacto de 128)" if i["sobrante"] == 0
                      else f"⚠ Sobran {i['sobrante']} bytes: archivo dañado")
        filas = [
            ("Ruta", i["ruta"]),
            ("Tamaño", f"{i['tamano']:,} bytes"),
            ("Registros", f"{i['registros']} × {TAM_REGISTRO} bytes"),
            ("Estructura", estructura),
            ("Modificado", i["modificado"]),
            ("Último acceso", i["accedido"]),
            ("Permisos", f"{i['permisos']}   ({i['octal']})"),
            ("Lectura", si_no(i["lectura"])),
            ("Escritura", si_no(i["escritura"])),
        ]
        tabla = "".join(f"<tr><td><b>{k}</b></td><td>{v}</td></tr>" for k, v in filas)
        QMessageBox.information(self, f"Información de {i['nombre']}",
                                f"<table cellpadding='4'>{tabla}</table>")

        # ================= Integridad =================
    def avisos_iniciales(self):
        """Se llama justo después de abrir la ventana."""
        if self.agenda.indice_reconstruido:
            QMessageBox.information(self, "Índice reconstruido",
                                    "indice.json no existía o estaba dañado.\n"
                                    "Se reconstruyó leyendo contactos.dat de forma secuencial.")
        if self.agenda.integridad[0] == "alterado":
            self.verificar_integridad()

    def verificar_integridad(self):
        estado, guardado, actual = verificar()
        self.agenda.integridad = (estado, guardado, actual)
        self.actualizar_integridad()
        if estado != "alterado":
            QMessageBox.information(self, "Integridad",
                                    f"El archivo no ha sido alterado.\n\nSHA-256:\n{actual}")
            return
        respuesta = QMessageBox.warning(
            self, "Archivo alterado",
            "contactos.dat fue modificado fuera de la aplicación.\n\n"
            f"Hash guardado:\n{guardado}\n\nHash actual:\n{actual}\n\n"
            "¿Aceptar el archivo como está y guardar la nueva huella?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            self.agenda.aceptar_estado_actual()
            self.actualizar_integridad()

    # ================= Apariencia y otros =================
    def aplicar_tema(self, nombre: str):
        """ Cambia colores y tipografías de toda la app en caliente """

        self.tema = TEMAS[nombre]
        QApplication.instance().setStyleSheet(construir_qss(self.tema))
        self.panel.set_tema(self.tema)
        self.formulario.set_tema(self.tema)
        self.actualizar_integridad()
        self.recargar()
        if self.id_editando is not None:          # conservar la fila seleccionada
            self.panel.seleccionar_id(self.id_editando)

    def acerca_de(self):
        QMessageBox.about(self, "Acerca de",
                          "<b>Agenda de Contactos</b><br>"
                          f"Registros de tamaño fijo ({TAM_REGISTRO} bytes), acceso aleatorio "
                          "con seek()/tell(), índice primario JSON e integridad SHA-256.<br><br>"
                          "Manejo e Implementación de Archivos · URL")