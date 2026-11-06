""" Temas visuales de la interfaz y construcción de la hoja de estilos (QSS) """

# Cada tema define su paleta, tipografías y radio de esquinas.
TEMAS = {
    "Tarjetero": {          # claro, como fichas de un tarjetero de oficina
        "fondo": "#E6ECF0", "panel": "#FFFFFF", "borde": "#CBD5DD", "alterna": "#F3F6F8",
        "texto": "#1B2A41", "suave": "#5E6E82",
        "acento": "#1B2A41", "sobre_acento": "#FFFFFF",
        "marca": "#E0A526", "ok": "#2F855A", "error": "#C53030",
        "fuente": "Avenir Next", "titulo": "Charter", "mono": "Menlo", "radio": 4,
    },
    "Bytes": {              # oscuro y técnico, centrado en posiciones de bytes
        "fondo": "#141827", "panel": "#1C2135", "borde": "#2C3350", "alterna": "#191E30",
        "texto": "#DCE3F5", "suave": "#8691B4",
        "acento": "#4CC9F0", "sobre_acento": "#0D1B2A",
        "marca": "#F7B267", "ok": "#5BD69A", "error": "#FF6B6B",
        "fuente": "Avenir Next", "titulo": "Avenir Next", "mono": "Menlo", "radio": 6,
    },
    "Aurora": {             # claro y suave, lila con acento violeta
        "fondo": "#F4F1FB", "panel": "#FFFFFF", "borde": "#E3DCF5", "alterna": "#FAF8FE",
        "texto": "#2A1B4D", "suave": "#7A6E99",
        "acento": "#6D3FE0", "sobre_acento": "#FFFFFF",
        "marca": "#E84A8A", "ok": "#1E9E6A", "error": "#D6336C",
        "fuente": "Avenir Next", "titulo": "Avenir Next", "mono": "Menlo", "radio": 14,
    },
}

def construir_qss(t: dict) -> str:
    """ Arma la hoja de estilos a partir de un tema """
    r = t["radio"]
    return f"""
    
QMainWindow {{ background-color: {t['fondo']}; }}
QWidget {{ color: {t['texto']}; font-family: "{t['fuente']}"; font-size: 13px; }}
QLabel {{ background: transparent; }}

/* Menú */
QMenuBar {{ background-color: {t['panel']}; border-bottom: 1px solid {t['borde']}; }}
QMenuBar::item {{ padding: 6px 12px; background: transparent; }}
QMenuBar::item:selected {{ background-color: {t['borde']}; border-radius: {r}px; }}
QMenu {{ background-color: {t['panel']}; border: 1px solid {t['borde']}; padding: 4px; }}
QMenu::item {{ padding: 6px 24px; border-radius: {r}px; }}
QMenu::item:selected {{ background-color: {t['acento']}; color: {t['sobre_acento']}; }}
QMenu::separator {{ height: 1px; background: {t['borde']}; margin: 4px 8px; }}

/* Barra lateral */
#lateral {{ background-color: {t['panel']}; border-right: 1px solid {t['borde']}; }}
#logo {{ font-family: "{t['titulo']}"; font-size: 24px; font-weight: bold; }}
#seccion {{ color: {t['suave']}; font-size: 12px; font-weight: 600; padding-top: 18px; }}
#lateral QPushButton {{ background: transparent; border: none; text-align: left;
    padding: 9px 12px; border-radius: {r}px; color: {t['texto']}; font-weight: normal; }}
#lateral QPushButton:hover {{ background-color: {t['fondo']}; }}

/* Tarjetas y títulos */
QFrame#tarjeta {{ background-color: {t['panel']}; border: 1px solid {t['borde']};
    border-radius: {r + 2}px; }}
#titulo {{ font-family: "{t['titulo']}"; font-size: 22px; font-weight: bold; }}
#subtitulo {{ color: {t['suave']}; }}
#bytes {{ background-color: {t['fondo']}; border: 1px solid {t['borde']};
    border-radius: {r}px; padding: 8px; }}
#dato {{ font-family: "{t['mono']}"; color: {t['suave']}; font-size: 12px; }}
#avatar {{ background-color: {t['marca']}; color: #FFFFFF;
    border-radius: 28px; font-size: 20px; font-weight: bold; }}

/* Campos */
QLineEdit {{ background-color: {t['fondo']}; border: 1px solid {t['borde']};
    border-radius: {r}px; padding: 8px 10px; selection-background-color: {t['acento']};
    selection-color: {t['sobre_acento']}; }}
QLineEdit:focus {{ border: 1px solid {t['acento']}; }}
QLineEdit:disabled {{ color: {t['suave']}; }}

/* Botones */
QPushButton {{ background-color: {t['acento']}; color: {t['sobre_acento']}; border: none;
    border-radius: {r}px; padding: 9px 16px; font-weight: 600; }}
QPushButton:hover {{ background-color: {t['marca']}; color: #FFFFFF; }}
QPushButton#secundario {{ background: transparent; border: 1px solid {t['borde']};
    color: {t['texto']}; }}
QPushButton#secundario:hover {{ background-color: {t['fondo']}; }}

/* Tabla */
QTableWidget {{ background-color: {t['panel']}; border: none;
    alternate-background-color: {t['alterna']};
    selection-background-color: {t['acento']}; selection-color: {t['sobre_acento']}; }}
QTableWidget::item {{ padding: 4px 6px; }}
QHeaderView::section {{ background-color: {t['panel']}; color: {t['suave']}; border: none;
    border-bottom: 2px solid {t['borde']}; padding: 9px 6px; font-weight: 600; }}
QTableCornerButton::section {{ background-color: {t['panel']}; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: {t['borde']}; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}

/* Barra de estado */
QStatusBar {{ background-color: {t['panel']}; border-top: 1px solid {t['borde']};
    color: {t['suave']}; }}
QStatusBar QLabel {{ padding: 0 10px; font-family: "{t['mono']}"; font-size: 12px; }}

QMessageBox {{ background-color: {t['panel']}; }}
QToolTip {{ background-color: {t['panel']}; color: {t['texto']}; border: 1px solid {t['borde']}; }}
"""