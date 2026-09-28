"""Sprite placeholder en pixel art (grilla 16x16) dibujado con Cairo.

Cada frame es una lista de 16 cadenas de 16 caracteres. Cada carácter es una
"celda" de 1x1 que se escala por SCALE (x4 por defecto). Una letra = un color,
definido en PALETTE. El carácter '.' es transparente.

El sprite es simétrico, así que `mirror_frame` no cambia nada visualmente por
ahora, pero se mantiene por si en el futuro se añade una cola o detalles
asimétricos.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Paleta base: letra -> color (r, g, b) en rango 0..1.
# 'O' es el color del cuerpo, que cambia según la "actividad" (ver BODY_COLORS).
# ---------------------------------------------------------------------------
PALETTE_BASE = {
    "K": (0.13, 0.12, 0.16),   # contorno (casi negro)
    "B": (0.04, 0.04, 0.07),   # ojos
    "P": (0.96, 0.52, 0.58),   # boca / rubor (rosa)
}

# Colores del cuerpo disponibles; se alternan al hacer clic.
BODY_COLORS = [
    (0.95, 0.58, 0.18),   # naranja
    (0.22, 0.72, 0.62),   # verde azulado
    (0.62, 0.42, 0.86),   # violeta
    (0.92, 0.50, 0.70),   # rosa
]

# ---------------------------------------------------------------------------
# Frames de 16x16. El carácter 'O' es el cuerpo (se colorea según la actividad).
# ---------------------------------------------------------------------------

# Caminar, cuadro A: patas separadas (posición de apoyo).
FRAME_WALK_A = (
    "................",
    "................",
    "....KKKKKKKK....",
    "...KOOOOOOOOK...",
    "..KOOOOOOOOOOK..",
    "..KOOBBOOBBOOK..",
    "..KOOOOOOOOOOK..",
    "..KOOOPPPPOOOK..",
    "..KOOOOOOOOOOK..",
    "...KOOOOOOOOK...",
    "....KKKKKKKK....",
    ".....K....K.....",
    ".....K....K.....",
    ".....K....K.....",
    ".....K....K.....",
    "................",
)

# Caminar, cuadro B: patas juntas (posición de paso).
FRAME_WALK_B = (
    "................",
    "................",
    "....KKKKKKKK....",
    "...KOOOOOOOOK...",
    "..KOOOOOOOOOOK..",
    "..KOOBBOOBBOOK..",
    "..KOOOOOOOOOOK..",
    "..KOOOPPPPOOOK..",
    "..KOOOOOOOOOOK..",
    "...KOOOOOOOOK...",
    "....KKKKKKKK....",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    "................",
)

# Salto: patas recogidas. Se dibuja mientras el sprite sube/baja.
FRAME_JUMP = (
    "................",
    "................",
    "................",
    "....KKKKKKKK....",
    "...KOOOOOOOOK...",
    "..KOOOOOOOOOOK..",
    "..KOOBBOOBBOOK..",
    "..KOOOOOOOOOOK..",
    "..KOOOPPPPOOOK..",
    "..KOOOOOOOOOOK..",
    "...KOOOOOOOOK...",
    "....KKKKKKKK....",
    "................",
    "................",
    "................",
    "................",
)

# Secuencia de caminata: se alterna A/B/A/B... para dar la ilusión de paso.
FRAMES_WALK = (FRAME_WALK_A, FRAME_WALK_B)

GRID_SIZE = 16


def mirror_frame(frame):
    """Devuelve el frame reflejado horizontalmente (para caminar hacia la izq.)."""
    return tuple(row[::-1] for row in frame)


def build_palette(body_index):
    """Devuelve el diccionario de colores completo para un índice de actividad."""
    palette = dict(PALETTE_BASE)
    palette["O"] = BODY_COLORS[body_index % len(BODY_COLORS)]
    return palette


def draw_frame(cr, frame, x, y, scale, palette):
    """Dibuja `frame` (16x16) con la esquina superior izquierda en (x, y)."""
    for row_idx, row in enumerate(frame):
        for col_idx, ch in enumerate(row):
            color = palette.get(ch)
            if color is None:
                continue
            cr.set_source_rgb(*color)
            cr.rectangle(
                x + col_idx * scale,
                y + row_idx * scale,
                scale,
                scale,
            )
            cr.fill()


class Sprite:
    """Estado y dibujo del sprite.

    - `x`, `y`: posición de la esquina superior izquierda del sprite en
      coordenadas de la ventana (píxeles lógicos).
    - `direction`: +1 hacia la derecha, -1 hacia la izquierda.
    - `scale`: factor de escala de la grilla (x4 por defecto -> 64px).
    """

    def __init__(self, scale=4):
        self.scale = scale
        self.width = GRID_SIZE * scale
        self.height = GRID_SIZE * scale
        self.x = 0.0
        self.y = 0.0
        self.direction = 1
        self.body_index = 0

    @property
    def palette(self):
        return build_palette(self.body_index)

    def rect(self):
        """Rectángulo del sprite (x, y, w, h) para la región de entrada."""
        return (int(self.x), int(self.y), self.width, self.height)

    def draw(self, cr, frame, direction=None):
        """Dibuja `frame` en la posición actual.

        Si `direction` es -1, se refleja el frame horizontalmente.
        """
        d = direction if direction is not None else self.direction
        if d < 0:
            frame = mirror_frame(frame)
        draw_frame(cr, frame, self.x, self.y, self.scale, self.palette)
