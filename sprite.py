"""Sprite en pixel art (grilla 16x16) dibujado con Cairo.

Admite múltiples personajes (Tux y la familia Koru: Koru, Clawd, Tuno, Nilo,
Brio, Luma, Mako, Orbi). Cada personaje define su propia grilla 16x16 y su
paleta de colores propia en `personajes.py`.
"""

from __future__ import annotations

import personajes

GRID_SIZE = 16

# Personaje por defecto para compatibilidad directa
_DEF_PERSONAJE = personajes.TUX

FRAME_WALK_A = _DEF_PERSONAJE.frames["walk_a"]
FRAME_WALK_B = _DEF_PERSONAJE.frames["walk_b"]
FRAMES_WALK = (FRAME_WALK_A, FRAME_WALK_B)
FRAME_JUMP = _DEF_PERSONAJE.frames["jump"]
FRAME_SIESTA = _DEF_PERSONAJE.frames["siesta"]
FRAME_SIESTA_Z = _DEF_PERSONAJE.frames["siesta_z"]
FRAME_LEER = _DEF_PERSONAJE.frames["leer"]
FRAME_CODIGO = _DEF_PERSONAJE.frames["codigo"]
FRAME_ESTIRAR = _DEF_PERSONAJE.frames["estirar"]
FRAMES_CARA = _DEF_PERSONAJE.caras

# Paleta base histórica (mantenida por compatibilidad)
PALETTE_BASE = personajes.PALETA_BASE_TINTAS
BODY_COLORS = [
    (0.95, 0.58, 0.18),   # naranja
    (0.22, 0.72, 0.62),   # verde azulado
    (0.62, 0.42, 0.86),   # violeta
    (0.92, 0.50, 0.70),   # rosa
]


def mirror_frame(frame):
    """Devuelve el frame reflejado horizontalmente (para caminar hacia la izq.)."""
    return tuple(row[::-1] for row in frame)


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
    - `personaje`: objeto `Personaje` activo de `personajes.py`.
    """

    def __init__(self, scale=4, personaje_id="tux", personaje=None):
        self.scale = scale
        self.width = GRID_SIZE * scale
        self.height = GRID_SIZE * scale
        self.x = 0.0
        self.y = 0.0
        self.direction = 1
        p_id = personaje if personaje is not None else personaje_id
        self.personaje = personajes.get_personaje(p_id)
        self.body_index = 0

    def set_personaje(self, nombre_o_id):
        """Cambia el personaje activo y su paleta."""
        self.personaje = personajes.get_personaje(nombre_o_id)

    cambiar_personaje = set_personaje

    @property
    def palette(self):
        return self.personaje.paleta

    @property
    def paleta(self):
        return self.personaje.paleta

    @property
    def frames(self):
        return self.personaje.frames


    @property
    def frame_jump(self):
        return self.personaje.frames["jump"]

    @property
    def frame_siesta(self):
        return self.personaje.frames["siesta"]

    @property
    def frame_siesta_z(self):
        return self.personaje.frames["siesta_z"]

    @property
    def frame_leer(self):
        return self.personaje.frames["leer"]

    @property
    def frame_codigo(self):
        return self.personaje.frames["codigo"]

    @property
    def frame_estirar(self):
        return self.personaje.frames["estirar"]

    def frame_walk(self, index):
        return self.personaje.frames["walk_a" if index % 2 == 0 else "walk_b"]

    def frame_cara(self, nombre):
        return self.personaje.caras.get(nombre, self.personaje.frames["walk_a"])

    def tiene_cara(self, nombre):
        return nombre in self.personaje.caras

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
