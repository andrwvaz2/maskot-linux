"""Interfaz común de los backends de ventana.

Cada backend se encarga de preparar la ventana para que se comporte como una
mascota flotante: sin bordes, siempre encima / anclada abajo, y con
click-through (el puntero atraviesa la ventana salvo encima del sprite).

El click-through se implementa con `Gdk.Surface.set_input_region`, que es la
API multiplataforma de GDK: en X11 se traduce a XShape (shape input) y en
Wayland a `wl_surface.set_input_region`. Esto nos evita hablar XShape o
wl_surface a mano en cada backend.
"""

from __future__ import annotations

import cairo
from gi.repository import Gdk


class Backend:
    """Backend base. Subclases: X11Backend y WaylandBackend."""

    name = "base"

    def __init__(self, window):
        self.window = window

    def setup(self):
        """Configura la ventana ANTES de mostrarla (decoración, capa, etc.)."""

    def on_mapped(self):
        """Se llama una sola vez cuando la ventana ya está mapeada.

        Útil para propiedades de bajo nivel (p. ej. _NET_WM_* en X11) que
        conviene aplicar con la ventana ya visible.
        """

    def set_input_region(self, rects):
        """Actualiza la región donde la ventana recibe el puntero.

        `rects` es un rectángulo (x, y, w, h), una lista de rectángulos, o
        `None` para vaciar la región (click-through total). Se llama cada vez
        que se mueve el sprite o el globo, así que la ventana solo recibe
        puntero justo encima de lo que se ve.
        """
        surface = self.window.get_surface()
        if surface is None:
            return
        if rects is None:
            region = cairo.Region()  # región vacía -> el clic atraviesa
        else:
            if isinstance(rects[0], int):   # un solo rectángulo
                rects = [rects]
            # Ojo: cairo.Region.union() MUTA la región y devuelve None.
            region = cairo.Region()
            for x, y, w, h in rects:
                if w <= 0 or h <= 0:
                    continue
                region.union(
                    cairo.Region(
                        cairo.RectangleInt(int(x), int(y), int(w), int(h))
                    )
                )
        surface.set_input_region(region)

    def cleanup(self):
        """Libera recursos si hace falta (p. ej. cierra conexiones X11)."""
