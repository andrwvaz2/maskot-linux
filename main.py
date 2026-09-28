"""Mascota de escritorio en pixel art (prototipo).

Valida la parte difícil: una ventana flotante transparente con click-through
que funciona en distintos escritorios Linux.

Uso:
    python3 main.py [--x11] [--scale N]

El backend se elige según el entorno ($XDG_SESSION_TYPE / $XDG_CURRENT_DESKTOP):
- Wayland con layer-shell (Sway, Hyprland, niri, river, ...) -> gtk4-layer-shell.
- X11 / XWayland -> ventana dock con XShape (via GDK) y propiedades EWMH.
- Wayland sin layer-shell (GNOME/KDE) -> ventana normal + aviso recomendando --x11.

Nota: se usa `GLib.MainLoop` en vez de `Gtk.Application` a propósito. El
registro DBus de Gtk.Application puede bloquearse en XWayland (carga del tema
de iconos) y la mascota no necesita ciclo de vida de aplicación.
"""

from __future__ import annotations

import argparse
import math
import os
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

from sprite import FRAMES_WALK, FRAME_JUMP, Sprite  # noqa: E402
from backends import X11Backend, WaylandBackend  # noqa: E402
from backends.wayland import HAS_LAYER_SHELL  # noqa: E402
from tray import Tray  # noqa: E402

# --- Parámetros de la animación --------------------------------------------

FPS = 20
TICK_MS = int(1000 / FPS)      # ~50 ms
SPEED = 4                       # px por tick (a 20 FPS = 80 px/s)
FRAME_INTERVAL = 3              # ticks entre cambio de cuadro de caminata
JUMP_TICKS = 8                  # duración del salto (8 ticks = 0.4 s)


def window_height_for(scale):
    # sprite (16*scale) + espacio de salto (8*scale) + margen inferior
    return 16 * scale + 8 * scale + 4


def detect_backend(force_x11):
    """Devuelve (nombre, motivo) del backend elegido."""
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    desktop_str = desktop or "desconocido"

    if force_x11:
        os.environ["GDK_BACKEND"] = "x11"
        return "x11", "forzado con --x11 (XWayland o X11)"

    if os.environ.get("GDK_BACKEND", "").lower() == "x11":
        return "x11", "GDK_BACKEND=x11 en el entorno"

    if session == "wayland":
        if HAS_LAYER_SHELL:
            return "wayland", (
                f"Wayland ({desktop_str}): se intenta gtk4-layer-shell"
            )
        return "wayland", (
            f"Wayland ({desktop_str}): gtk4-layer-shell NO está instalado"
        )

    return "x11", f"sesión '{session or 'desconocida'}' (X11/XWayland)"


class Mascota:
    def __init__(self, backend_name, scale):
        self.backend_name = backend_name
        self.scale = scale
        self.window_height = window_height_for(scale)
        self.sprite = Sprite(scale)

        self.backend = None
        self.tray = None
        self.loop = None
        self.window = None
        self.drawing_area = None
        self.window_width = 0

        # estado de la animación
        self.state = "walk"
        self.direction = 1
        self.walk_frame = 0
        self.walk_tick = 0
        self.jump_t = 0.0

    # ------------------------------------------------------------------ setup

    def run(self):
        Gtk.init()
        self._apply_transparent_css()
        self._build_window()
        self._setup_backend()

        gesture = Gtk.GestureClick.new()
        gesture.connect("pressed", self.on_pressed)
        self.drawing_area.add_controller(gesture)

        self.window.connect("map", self.on_map)
        self.window.connect("close-request", self.on_close_request)

        self.tray = Tray(on_toggle=self.on_tray_toggle, on_quit=self.on_tray_quit)

        self._reset_sprite()
        self.window.present()
        GLib.timeout_add(TICK_MS, self.tick)

        self.loop = GLib.MainLoop()
        try:
            self.loop.run()
        finally:
            if self.tray is not None:
                self.tray.shutdown()

    def _build_window(self):
        self.window = Gtk.Window()
        self.window.set_title("Mascota")

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.on_draw)
        self.window.set_child(self.drawing_area)

    def _setup_backend(self):
        if self.backend_name == "x11":
            self.backend = X11Backend(self.window)
            self._configure_x11_geometry()
        else:
            self.backend = WaylandBackend(self.window)
            self.window.set_default_size(0, self.window_height)

        self.backend.setup()

    def _configure_x11_geometry(self):
        """Tamaño y posición del dock X11 según el monitor primario."""
        display = Gdk.Display.get_default()
        monitor = self._primary_monitor(display)
        if monitor is None:
            return
        geo = monitor.get_geometry()
        height = self.window_height
        x = geo.x
        y = geo.y + geo.height - height
        self.window.set_default_size(geo.width, height)
        # El backend moverá la ventana con XMoveWindow al mapearse.
        self.backend.pending_move = (x, y, geo.width, height)

    @staticmethod
    def _primary_monitor(display):
        if display is None:
            return None
        monitors = display.get_monitors()
        if not monitors:
            return None
        # GDK4 no expone "monitor primario"; usamos el primero (suele bastar).
        return monitors[0]

    def _apply_transparent_css(self):
        css = b"window { background-color: transparent; }"
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _reset_sprite(self):
        self.sprite.x = 0.0
        self.sprite.y = self._ground_y()
        self.direction = 1
        self.state = "walk"
        self.walk_frame = 0
        self.jump_t = 0.0

    def _ground_y(self):
        return self.window_height - 4 - self.sprite.height

    # ------------------------------------------------------------- callbacks

    def on_map(self, window):
        if self.backend is not None:
            self.backend.on_mapped()

    def on_close_request(self, window):
        # Ocultamos en vez de destruir (la app se cierra por la bandeja).
        window.set_visible(False)
        return True

    def on_pressed(self, gesture, n_press, x, y):
        if self.state != "jump":
            self.state = "jump"
            self.jump_t = 0.0

    def on_draw(self, area, cr, width, height):
        self.window_width = width
        if self.state == "jump":
            frame = FRAME_JUMP
        else:
            frame = FRAMES_WALK[self.walk_frame]
        self.sprite.draw(cr, frame)

    def on_tray_toggle(self, visible):
        self.window.set_visible(visible)

    def on_tray_quit(self):
        self.quit()

    def quit(self):
        if self.loop is not None:
            self.loop.quit()

    # ------------------------------------------------------------ animación

    def tick(self):
        if self.state == "walk":
            self._tick_walk()
        else:
            self._tick_jump()

        if self.backend is not None:
            self.backend.set_input_region(self.sprite.rect())
        self.drawing_area.queue_draw()
        return True

    def _tick_walk(self):
        self.sprite.x += SPEED * self.direction

        max_x = max(0, self.window_width - self.sprite.width)
        if self.sprite.x <= 0:
            self.sprite.x = 0
            self.direction = 1
        elif self.sprite.x >= max_x:
            self.sprite.x = max_x
            self.direction = -1

        self.sprite.direction = self.direction
        self.walk_tick += 1
        if self.walk_tick >= FRAME_INTERVAL:
            self.walk_tick = 0
            self.walk_frame = 1 - self.walk_frame  # alterna A/B

    def _tick_jump(self):
        self.jump_t += 1.0 / JUMP_TICKS
        if self.jump_t >= 1.0:
            # fin del salto: volver a caminar y cambiar de actividad/color
            self.state = "walk"
            self.sprite.y = self._ground_y()
            self.sprite.body_index += 1
            self.walk_frame = 0
            self.walk_tick = 0
        else:
            t = self.jump_t
            altura = self.scale * 8
            self.sprite.y = self._ground_y() - altura * math.sin(math.pi * t)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Mascota de escritorio en pixel art")
    parser.add_argument("--x11", action="store_true",
                        help="forzar el backend X11 (XWayland)")
    parser.add_argument("--scale", type=int, default=4,
                        help="escala de la grilla 16x16 (por defecto 4)")
    args = parser.parse_args(argv)

    # GDK lee $GDK_BACKEND al abrir el display, y eso ocurre al inicializar GTK,
    # que ya está cargado cuando estamos aquí. Por eso, si piden --x11 sin la
    # variable puesta, nos re-ejecutamos con ella (una sola vez).
    if args.x11 and os.environ.get("GDK_BACKEND") != "x11":
        os.environ["GDK_BACKEND"] = "x11"
        _argv = sys.argv[1:] if argv is None else list(argv)
        # -u se conserva para que la salida siga apareciendo sin delay.
        os.execv(sys.executable, [sys.executable, "-u", os.path.abspath(__file__), *_argv])

    backend_name, reason = detect_backend(args.x11)
    print(f"[main] sesión: XDG_SESSION_TYPE={os.environ.get('XDG_SESSION_TYPE')!r}, "
          f"XDG_CURRENT_DESKTOP={os.environ.get('XDG_CURRENT_DESKTOP')!r}")
    print(f"[main] backend elegido: {backend_name} ({reason})")

    Mascota(backend_name, args.scale).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
