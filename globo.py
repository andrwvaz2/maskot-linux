"""Globo de texto dibujado con Cairo sobre el sprite.

El globo es "hablado": se muestra un texto y se desvanece solo. Su rectángulo
se incluye en la región de entrada de la ventana (junto con el del sprite) para
que el texto siga siendo interactivo y para que el click-through del resto de
la ventana no se rompa.

El texto se dibuja con el "toy font" de Cairo (sin depender de Pango ni de
tipografías del sistema), por eso el tamaño se mide con `text_extents`.
"""

from __future__ import annotations

import math

# Colores del globo (rgba). `_con_alpha` aplica el desvanecido final.
FONDO = (0.99, 0.99, 0.99, 0.95)
BORDE = (0.20, 0.20, 0.26, 0.95)
TEXTO = (0.10, 0.10, 0.14, 1.0)
SOMBRA = (0.0, 0.0, 0.0, 0.12)


def _con_alpha(color, alpha):
    return (color[0], color[1], color[2], color[3] * alpha)

# Alto del cuerpo de texto en píxeles lógicos (se ajusta con la escala).
ALTO_TEXTO_BASE = 11


class Globo:
    """Globo de texto con vida finita."""

    def __init__(self, scale=4):
        self.scale = scale
        self.texto = ""
        self.ms_restantes = 0
        self.ms_totales = 0
        self.x = 0.0
        self.y = 0.0
        self.ancho = 0
        self.alto = 0

    # -- ciclo de vida -------------------------------------------------------

    @property
    def visible(self):
        return self.ms_restantes > 0 and bool(self.texto)

    def mostrar(self, texto, ms=3500, x=0.0, y=0.0):
        """Pone texto en el globo durante `ms` milisegundos."""
        texto = (texto or "").strip()
        if not texto:
            return False
        self.texto = texto
        self.ms_totales = max(400, int(ms))
        self.ms_restantes = self.ms_totales
        self.x = float(x)
        self.y = float(y)
        self.alto = self._alto_linea() + 10
        return True

    def ocultar(self):
        self.texto = ""
        self.ms_restantes = 0

    def tick(self, dt_ms):
        if self.ms_restantes > 0:
            self.ms_restantes = max(0, self.ms_restantes - int(dt_ms))

    # -- geometría -----------------------------------------------------------

    def _alto_linea(self):
        return max(9, int(ALTO_TEXTO_BASE * max(1, self.scale / 4)))

    def _medir(self, cr):
        """Mide el texto y devuelve (ancho, alto, x_text, y_text)."""
        cr.select_font_face("sans", 0, 0)
        cr.set_font_size(self._alto_linea())
        ext = cr.text_extents(self.texto)
        ancho = int(math.ceil(ext[2])) + 12   # +6 de margen a cada lado
        alto = self.alto
        return ancho, alto, 6, self._alto_linea()

    def _colocar(self, sprite_x, sprite_y, sprite_w, sprite_h, ancho, alto,
                 limit_w):
        """Coloca el globo encima del sprite y lo recorta a la ventana."""
        self.ancho = ancho
        self.alto = alto
        x = sprite_x + sprite_w / 2 - ancho / 2
        y = sprite_y - alto - 4          # 4 px de "cuello" hacia el sprite
        self.x = max(0, min(x, max(0, limit_w - ancho)))
        self.y = max(0, y)
        return self.x, self.y

    def rect(self):
        """Rectángulo del globo (incluye el rabito) o None si no se ve."""
        if not self.visible:
            return None
        return (int(self.x), int(self.y), int(self.ancho), int(self.alto + 5))

    # -- dibujo -------------------------------------------------------------

    def dibujar(self, cr, sprite_rect, limit_w, alpha=1.0):
        """Dibuja el globo apuntando al sprite. Devuelve su rectángulo o None."""
        if not self.visible:
            return None
        ancho, alto, tx, ty = self._medir(cr)
        sx, sy, sw, sh = sprite_rect
        self._colocar(sx, sy, sw, sh, ancho, alto, limit_w)

        # Desvanecido en el último 25 % del tiempo.
        if self.ms_restantes < self.ms_totales * 0.25:
            alpha = min(alpha, max(0.0, self.ms_restantes / (self.ms_totales * 0.25)))

        cr.save()
        cr.set_operator(1)  # OVER
        if alpha < 1.0:
            cr.push_group()

        x, y = self.x, self.y
        radio = max(3, min(8, alto // 2))
        # Sombra
        cr.set_source_rgba(*_con_alpha(SOMBRA, alpha))
        _redondeado(cr, x + 1, y + 2, self.ancho, alto, radio)
        cr.fill()
        # Cuerpo
        cr.set_source_rgba(*_con_alpha(FONDO, alpha))
        _redondeado(cr, x, y, self.ancho, alto, radio)
        cr.fill()
        # Rabito hacia el centro del sprite
        cr.move_to(x + self.ancho / 2 - 4, y + alto)
        cr.line_to(x + self.ancho / 2, y + alto + 5)
        cr.line_to(x + self.ancho / 2 + 4, y + alto)
        cr.close_path()
        cr.fill()
        # Borde
        cr.set_source_rgba(*_con_alpha(BORDE, alpha))
        cr.set_line_width(1.0)
        _redondeado(cr, x + 0.5, y + 0.5, self.ancho - 1, alto - 1, radio)
        cr.stroke()

        cr.select_font_face("sans", 0, 0)
        cr.set_font_size(self._alto_linea())
        cr.set_source_rgba(*_con_alpha(TEXTO, alpha))
        cr.move_to(x + tx, y + ty)
        cr.show_text(self.texto)

        if alpha < 1.0:
            cr.pop_group_to_source()
            cr.paint_with_alpha(alpha)
        cr.restore()
        return self.rect()


def _redondeado(cr, x, y, w, h, r):
    """Añade a la ruta actual un rectángulo con esquinas redondeadas."""
    r = max(0, min(r, w / 2, h / 2))
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()
