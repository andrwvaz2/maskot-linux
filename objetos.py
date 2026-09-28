"""Objetos PIXel-art que la mascota puede usar o tener cerca.

Se dibujan con el mismo mecanismo que el sprite (grilla de caracteres + paleta
+ `draw_frame`), así que los objetos encajan con el estilo sin código extra.

Objetos definidos: `banca`, `libro`, `taza`, `portatil`.
Cada uno es una lista de cadenas; `.` es transparente. La posición que se le
pasa a `dibujar` es la esquina superior izquierda, en píxeles de la ventana.
"""

from __future__ import annotations

from sprite import draw_frame

# Paleta propia de los objetos (independiente de la del cuerpo del sprite).
PALETTE_OBJETOS = {
    "M": (0.55, 0.36, 0.22),   # madera
    "m": (0.40, 0.25, 0.15),   # madera oscura
    "K": (0.13, 0.12, 0.16),   # contorno
    "B": (0.04, 0.04, 0.07),   # negro (pantalla, tinta)
    "P": (0.96, 0.52, 0.58),   # rosa
    "G": (0.85, 0.88, 0.92),   # gris claro (página, vaho)
    "W": (0.98, 0.98, 0.98),   # blanco
    "C": (0.72, 0.50, 0.28),   # café
    "S": (0.35, 0.55, 0.85),   # azul (tapa, agua)
}

# --- banca: 16x8 -------------------------------------------------------------
BANCA = (
    "MMMMMMMMMMMMMMMM",
    "MmmmmmmmmmmmmmmM",
    "KMMMMMMMMMMMMMMK",
    ".KMMMMMMMMMMMMK.",
    "..K..K....K..K..",
    "..K..K....K..K..",
    "..K..K....K..K..",
    "..KKKK....KKKK..",
)

# --- libro: 8x8 (abierto, se lee desde arriba) ------------------------------
LIBRO = (
    "WWWWWWWW",
    "WGGGGGGW",
    "WGKGGKGW",
    "WGGGGGGW",
    "WGKGGKGW",
    "WGGGGGGW",
    "WmmmmmmW",
    "WWWWWWWW",
)

# --- taza de café: 8x8 -------------------------------------------------------
TAZA = (
    "..WW..",
    ".WCCW.",
    "WCCCCW",
    "WCCCCW",
    "WmmmmW",
    "WWWWWW",
    ".WWWW.",
    "..KK..",
)

# --- portátil: 12x8 ----------------------------------------------------------
PORTATIL = (
    "..KKKKKKKK..",
    ".KBBBBBBBBK.",
    ".KBWWWWWWBK.",
    ".KBWKKKKWBK.",
    ".KBBBBBBBBK.",
    "..KBBBBBBK..",
    "..KmmmmmmK..",
    "..KKKKKKKK..",
)

OBJETOS = {
    "banca": BANCA,
    "libro": LIBRO,
    "taza": TAZA,
    "portatil": PORTATIL,
}

# Tamaño en celdas de cada objeto, para poder colocarlos centrados.
TAMANOS = {nombre: (len(filas[0]), len(filas)) for nombre, filas in OBJETOS.items()}


def dibujar(cr, nombre, x, y, scale, alpha=1.0):
    """Dibuja el objeto `nombre` con su esquina superior izquierda en (x, y).

    Devuelve el rectángulo (x, y, w, h) en píxeles, o None si no existe.
    """
    filas = OBJETOS.get(nombre)
    if filas is None:
        return None
    if alpha < 1.0:
        cr.push_group()
    draw_frame(cr, filas, int(x), int(y), scale, PALETTE_OBJETOS)
    if alpha < 1.0:
        cr.pop_group_to_source()
        cr.paint_with_alpha(alpha)
    ancho, alto = TAMANOS[nombre]
    return (int(x), int(y), ancho * scale, alto * scale)
