"""Backend para Wayland usando gtk4-layer-shell (compositores wlroots/Smithay).

Coloca la ventana en la capa OVERLAY anclada abajo/izquierda/derecha (ancho
completo del monitor) y con modo de teclado NONE.

El click-through se implementa con `Gdk.Surface.set_input_region` (que en
Wayland equivale a `wl_surface.set_input_region`). gtk4-layer-shell NO expone
una API propia para la región de entrada; por eso la gestiona la clase base
con GDK, que sí funciona sobre una layer-surface.

Si gtk4-layer-shell no está instalado o el compositor no soporta
zwlr_layer_shell_v1 (p. ej. GNOME Wayland), se cae a una ventana normal sin
anclaje y se avisa por consola (ver `uses_layer_shell()`).
"""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk  # noqa: E402

from backends.base import Backend  # noqa: E402

try:
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gtk4LayerShell  # noqa: E402
    HAS_LAYER_SHELL = True
except (ImportError, ValueError):
    Gtk4LayerShell = None
    HAS_LAYER_SHELL = False


class WaylandBackend(Backend):
    name = "wayland"

    def __init__(self, window, prefer_layer_shell=True):
        super().__init__(window)
        self._want_layer_shell = prefer_layer_shell and HAS_LAYER_SHELL
        self._is_layer_shell = False

    def setup(self):
        self.window.set_decorated(False)
        self.window.set_resizable(False)

        if not self._want_layer_shell:
            self._warn_no_layer_shell()
            return

        if not Gtk4LayerShell.is_supported():
            self._is_layer_shell = False
            protocol = Gtk4LayerShell.get_protocol_version()
            if protocol > 0:
                # El compositor SÍ soporta layer-shell, pero el shim de
                # libwayland no se pudo inicializar (orden de carga). Suele
                # resolverse con LD_PRELOAD, ver README.
                print(
                    "[wayland] el compositor soporta layer-shell, pero "
                    "gtk4-layer-shell no se pudo inicializar (se cargó después "
                    "de libwayland).\n"
                    "          Prueba: LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so "
                    "python3 main.py"
                )
            else:
                self._warn_no_layer_shell()
            return

        w = self.window
        Gtk4LayerShell.init_for_window(w)
        Gtk4LayerShell.set_namespace(w, "mascota")
        Gtk4LayerShell.set_layer(w, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_keyboard_mode(w, Gtk4LayerShell.KeyboardMode.NONE)
        Gtk4LayerShell.set_exclusive_zone(w, 0)
        for edge in (
            Gtk4LayerShell.Edge.BOTTOM,
            Gtk4LayerShell.Edge.LEFT,
            Gtk4LayerShell.Edge.RIGHT,
        ):
            Gtk4LayerShell.set_anchor(w, edge, True)
        self._is_layer_shell = True
        print(
            "[wayland] layer-shell OK: capa OVERLAY, anclada abajo/izq/der, "
            "keyboard NONE"
        )

    def uses_layer_shell(self):
        return self._is_layer_shell

    def _warn_no_layer_shell(self):
        print(
            "[wayland] gtk4-layer-shell no está disponible o el compositor no "
            "soporta zwlr_layer_shell_v1.\n"
            "          La ventana se muestra sin anclaje (sin siempre-encima ni "
            "posición fija).\n"
            "          Recomendación: ejecuta con --x11 (o GDK_BACKEND=x11) "
            "para usar XWayland."
        )
