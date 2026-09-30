"""Objetos PIXel-art que la mascota puede usar o tener cerca.

Se dibujan con el mismo mecanismo que el sprite (grilla de caracteres + paleta
+ `draw_frame`), así que los objetos encajan con el estilo sin código extra.

Objetos definidos: `banca`, `libro`, `taza`, `portatil`, `papelera`, `hoja`,
`regadera` y la plantita en sus tres etapas (`planta_semilla`, `planta_brote`,
`planta_flor`).
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
    "B": (0.04, 0.04, 0.07),   # negro (pantalla, tinta, hueco)
    "P": (0.96, 0.52, 0.58),   # rosa
    "G": (0.85, 0.88, 0.92),   # gris claro (página, vaho, metal)
    "D": (0.45, 0.48, 0.55),   # gris medio (metal en sombra)
    "W": (0.98, 0.98, 0.98),   # blanco
    "C": (0.72, 0.50, 0.28),   # café
    "S": (0.35, 0.55, 0.85),   # azul (tapa, agua)
    "A": (0.55, 0.78, 0.93),   # agua (regadera)
    "T": (0.82, 0.48, 0.31),   # maceta (terracota)
    "t": (0.60, 0.33, 0.20),   # maceta en sombra
    "V": (0.30, 0.68, 0.36),   # verde de la hoja
    "v": (0.18, 0.47, 0.25),   # verde en sombra
    "F": (0.95, 0.45, 0.62),   # pétalos
    "f": (0.98, 0.82, 0.30),   # corazón de la flor
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

# --- papelera: 10x10 ---------------------------------------------------------
# Cubo metálico con la boca oscura; la hoja acaba "dentro" (se dibuja encima).
PAPELERA = (
    "KKKKKKKKKK",
    "KGGGGGGGGK",
    "KGBBBBBBGK",
    ".KGBBBBBK.",
    ".KGDDDDDG.",
    ".KGDDDDDG.",
    ".KGDDDDDG.",
    ".KGDDDDDG.",
    "..KGDDDG..",
    "..KKKKKK..",
)

# --- hoja de papel en el suelo: 8x5 ------------------------------------------
HOJA = (
    ".WWWWWW.",
    "WWWWWWWW",
    "WWllWWll",
    "WWllWWll",
    ".WWWWWW.",
)

# --- regadera: 10x8 (asa a la izquierda, pico con gota arriba a la derecha) ---
REGADERA = (
    ".........S",
    "........KA",
    ".......KA.",
    "G....KA...",
    "GG..KA....",
    "GGGKAAAAAK",
    ".GKAAAAAK.",
    "..KKKKKKK.",
)

# --- plantita: la maceta es igual en las 3 etapas; lo que crece es la planta --

# Etapa 1: semilla, un brote diminuto (10x10)
PLANTA_SEMILLA = (
    "..........",
    "..........",
    "..........",
    "..........",
    ".....VV...",
    ".....VV...",
    "....TTTT..",
    "..TTTTTT..",
    ".TTTTTTTT.",
    ".TttttttT.",
)

# Etapa 2: brote con dos hojas (10x12)
PLANTA_BROTE = (
    "..........",
    "..........",
    "..........",
    "..V....V..",
    "..VV..VV..",
    "...VVVV...",
    "...VV.....",
    "...VV.....",
    "....TTTT..",
    "..TTTTTT..",
    ".TTTTTTTT.",
    ".TttttttT.",
)

# Etapa 3: florecida (10x14)
PLANTA_FLOR = (
    "..........",
    "...FFFF...",
    "..FffffF..",
    "..FffffF..",
    "...FFFF...",
    "....VV....",
    "...VVVV...",
    "..V.VV.V..",
    "....VV....",
    "....VV....",
    "....TTTT..",
    "..TTTTTT..",
    ".TTTTTTTT.",
    ".TttttttT.",
)

OBJETOS = {
    "banca": BANCA,
    "libro": LIBRO,
    "taza": TAZA,
    "portatil": PORTATIL,
    "papelera": PAPELERA,
    "hoja": HOJA,
    "regadera": REGADERA,
    "planta_semilla": PLANTA_SEMILLA,
    "planta_brote": PLANTA_BROTE,
    "planta_flor": PLANTA_FLOR,
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
