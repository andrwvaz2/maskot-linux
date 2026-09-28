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

    def set_input_region(self, rect):
        """Actualiza la región donde la ventana recibe el puntero.

        `rect` es (x, y, w, h) en coordenadas de la ventana, o `None` para
        vaciar la región (click-through total). Se llama cada vez que el
        sprite se mueve.
        """
        surface = self.window.get_surface()
        if surface is None:
            return
        if rect is None:
            region = cairo.Region()  # región vacía -> el clic atraviesa
        else:
            x, y, w, h = rect
            region = cairo.Region(cairo.RectangleInt(int(x), int(y), int(w), int(h)))
        surface.set_input_region(region)

    def cleanup(self):
        """Libera recursos si hace falta (p. ej. cierra conexiones X11)."""
