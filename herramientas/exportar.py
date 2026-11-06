""" Exportación: contactos.dat -> JSON -> reporte PDF """
import json
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace

from nucleo.config import EXPORT_DIR, ENCODING, TAM_REGISTRO, ARCHIVO_CONTACTOS


def exportar_json(agenda, ruta: Path = EXPORT_DIR / "contactos.json") -> Path:
    """ Lee todos los contactos (lectura secuencial) y los guarda en JSON """

    contactos = [c.a_dict() for c in agenda.listar()]
    datos = {
        "generado": datetime.now().isoformat(timespec="seconds"),
        "origen": ARCHIVO_CONTACTOS.name,
        "tam_registro": TAM_REGISTRO,
        "total": len(contactos),
        "contactos": contactos,
    }
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(".tmp")                 # escritura segura
    with open(temporal, "w", encoding=ENCODING) as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
    temporal.replace(ruta)
    return ruta

class ReportePDF(FPDF):
    """PDF con encabezado y pie de página en todas las hojas."""

    def __init__(self, generado: str):
        super().__init__(orientation="L", format="Letter")   # horizontal: caben las columnas
        self.generado = generado
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Agenda de Contactos", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f"Reporte generado el {self.generado}", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"Página {self.page_no()}/{{nb}}", align="C")


def _texto(valor) -> str:
    """Las fuentes base del PDF solo aceptan Latin-1 (tildes y ñ sí; emojis no)."""
    return str(valor).encode("latin-1", "replace").decode("latin-1")


def exportar_pdf(ruta_json: Path = EXPORT_DIR / "contactos.json",
                 ruta_pdf: Path = EXPORT_DIR / "reporte_contactos.pdf") -> Path:
    """Genera el reporte PDF a partir del JSON exportado."""
    with open(ruta_json, "r", encoding=ENCODING) as f:
        datos = json.load(f)

    generado = datetime.fromisoformat(datos["generado"]).strftime("%d/%m/%Y %H:%M:%S")
    pdf = ReportePDF(generado)
    pdf.alias_nb_pages()                     # permite "Página 1/3"
    pdf.add_page()

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _texto(f"Total de contactos: {datos['total']}     "
                          f"Origen: {datos['origen']} (registros de {datos['tam_registro']} bytes)"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    encabezado_estilo = FontFace(emphasis="BOLD", color=255, fill_color=(28, 33, 53))
    with pdf.table(col_widths=(18, 55, 35, 70, 50), text_align="LEFT", line_height=7,
                   headings_style=encabezado_estilo,
                   cell_fill_color=(240, 243, 248), cell_fill_mode="ROWS") as tabla:
        encabezado = tabla.row()
        for titulo in ("ID", "Nombre", "Teléfono", "Correo", "Ciudad"):
            encabezado.cell(_texto(titulo))
        for c in datos["contactos"]:
            fila = tabla.row()
            for clave in ("id", "nombre", "telefono", "correo", "ciudad"):
                fila.cell(_texto(c[clave]))

    ruta_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(ruta_pdf))
    return ruta_pdf