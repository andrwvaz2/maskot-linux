"""Mascota de escritorio en pixel art.

Fase 1: ventana flotante, transparente y con click-through.
Fase 2: rutinas, globo de texto, pomodoro, pausa activa, API HTTP y preferencias.

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
import queue
import sys
import time

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

import objetos  # noqa: E402
import personajes  # noqa: E402
import sprite as sp  # noqa: E402
from api import ApiLocal  # noqa: E402
from backends import X11Backend, WaylandBackend  # noqa: E402
from backends.wayland import HAS_LAYER_SHELL  # noqa: E402
from globo import Globo  # noqa: E402
from pausa import PausaActiva  # noqa: E402
from pomodoro import FORMATOS, FASE_TRABAJO, Pomodoro  # noqa: E402
from preferencias import PERSONAJES, Preferencias  # noqa: E402
from rutinas import RUTINAS, MotorRutinas  # noqa: E402
from tray import Tray  # noqa: E402

# --- Parámetros de la animación --------------------------------------------

FPS = 20
TICK_MS = int(1000 / FPS)      # ~50 ms
FPS_DORMIDO = 5                # la siesta va a 5 FPS para no gastar CPU
SPEED = 4                       # px por tick (a 20 FPS = 80 px/s)
FRAME_INTERVAL = 3              # ticks entre cambio de cuadro de caminata
JUMP_TICKS = 8                  # duración del salto (8 ticks = 0.4 s)
MS_POR_TICK = 50                # referencia de movimiento del motor
INTERVALO_MENU_MS = 1000       # cada cuánto se refresca el menú de la bandeja
MS_SNAPSHOT_API = 500           # cada cuánto se refresca la instantánea HTTP

# IDs del menú de la bandeja (compartidos con la API interna).
ID_TOGGLE = 1
ID_QUIT = 2
ID_POM_ESTADO = 10
ID_POM_FORMATO_BASE = 11        # 11, 12, 13 -> 25/5, 45/10, 50/10
ID_POM_INICIAR = 14
ID_POM_PAUSAR = 15
ID_POM_SALTAR = 16
ID_RUT_ESTADO = 20
ID_RUT_BASE = 21                # 21..24 -> las cuatro rutinas
ID_RUT_ALEATORIA = 25
ID_PERSONAJE_ESTADO = 30
ID_PERSONAJE_BASE = 31          # 31..34
ID_API = 40
ID_POMODORO_PAUSA = 41


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
        self.sprite = sp.Sprite(scale)

        self.backend = None
        self.tray = None
        self.loop = None
        self.window = None
        self.drawing_area = None
        self.window_width = 0

        # estado de la animación (fase 1)
        self.state = "walk"
        self.direction = 1
        self.walk_frame = 0
        self.walk_tick = 0
        self.jump_t = 0.0

        # fase 2
        self.prefs = Preferencias()
        self.globo = Globo(scale)
        self.pomodoro = Pomodoro(self.prefs.get("formato_pomodoro", "25/5"),
                                 on_cambio=self.on_cambio)
        self.motor = MotorRutinas(self)
        self.pausa = PausaActiva(self, activo=bool(self.prefs.get("pausa_activa")))
        self.api = ApiLocal(self.estado_api, self.accion_api,
                            puerto=int(self.prefs.get("api_puerto", 7777)))
        self._cola_api = queue.Queue()
        self._estado_cache = {}
        self.pose_extra = None          # "estirar" (pausa activa)
        self.fps_objetivo = FPS
        self._intervalo_actual = TICK_MS
        self._tick_id = None
        self._ultimo_tick_ms = 0
        self._ultimo_pausa_ms = 0
        self._ultimo_snapshot_ms = 0
        self._ultimo_globo_ms = 0

        # personaje elegido en preferencias
        self._aplicar_personaje(self.prefs.personaje)

    def _aplicar_personaje(self, nombre):
        self.sprite.set_personaje(nombre)

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

        self.tray = Tray(app=self, on_toggle=self.on_tray_toggle,
                         on_quit=self.on_tray_quit)

        self._reset_sprite()
        self.window.present()
        self._ultimo_tick_ms = self._ahora_ms()
        self._ultimo_pausa_ms = self._ultimo_tick_ms
        self._ultimo_snapshot_ms = self._ultimo_tick_ms
        self._reprogramar_tick()
        GLib.timeout_add(INTERVALO_MENU_MS, self._refrescar_menu)

        print(f"[mascota] personaje: {self.prefs.personaje} | "
              f"días de uso: {self.prefs.dias_uso}")

        self.loop = GLib.MainLoop()
        try:
            self.loop.run()
        finally:
            if self.api.activo:
                self.api.parar()
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

    def suelo_y(self):
        """Altura del suelo (para apoyar objetos)."""
        return self._ground_y() + self.sprite.height

    def max_x(self):
        return max(0, self.window_width - self.sprite.width)

    # ------------------------------------------------- interfaz con el motor

    def saltar(self):
        self.state = "jump"
        self.jump_t = 0.0

    def poner_fps(self, n):
        """Fija la frecuencia de animación (None = la normal)."""
        nuevo = int(n) if n else FPS
        nuevo = max(1, min(60, nuevo))
        if nuevo == self.fps_objetivo:
            return
        self.fps_objetivo = nuevo
        self._reprogramar_tick()

    def poner_pose(self, nombre):
        self.pose_extra = nombre

    def cancelar_rutina(self, motivo=""):
        self.motor.cancelar(motivo)

    def on_cambio(self):
        """Algo cambió y el menú/estado deben refrescarse."""
        self.tray.refrescar() if self.tray else None
        self._refrescar_snapshot()

    # ------------------------------------------------------------- callbacks

    def on_map(self, window):
        if self.backend is not None:
            self.backend.on_mapped()

    def on_close_request(self, window):
        # Ocultamos en vez de destruir (la app se cierra por la bandeja).
        window.set_visible(False)
        return True

    def on_pressed(self, gesture, n_press, x, y):
        # Un clic despierta a la mascota y la hace saltar.
        if self.motor.activo:
            self.motor.cancelar("clic")
        if self.state != "jump":
            self.state = "jump"
            self.jump_t = 0.0

    def on_draw(self, area, cr, width, height):
        self.window_width = width
        self._draw_scene(cr, width)

    def _draw_scene(self, cr, width):
        # 1) Objetos colocados por la rutina (banca, libro, taza, portátil).
        for nombre, (ox, oy) in self.motor.objetos.items():
            objetos.dibujar(cr, nombre, ox, oy, self.scale)

        # 2) El sprite, con la pose que toque ahora mismo.
        frame = self.motor.frame_actual(self._frame_paseo())
        if self.pose_extra == "estirar":
            frame = self.sprite.frame_estirar
        self.sprite.draw(cr, frame)

        # 3) El globo de texto encima.
        self.globo.dibujar(cr, self.sprite.rect(), width)

    def _frame_paseo(self):
        if self.state == "jump":
            return self.sprite.frame_jump
        return self.sprite.frame_walk(self.walk_frame)

    def on_tray_toggle(self, visible):
        self.window.set_visible(visible)

    def on_tray_quit(self):
        self.quit()

    def quit(self):
        self.prefs.guardar()
        if self.loop is not None:
            self.loop.quit()

    # ------------------------------------------------------------ animación

    @staticmethod
    def _ahora_ms():
        return int(time.monotonic() * 1000)

    def _reprogramar_tick(self):
        if self._tick_id is not None:
            GLib.source_remove(self._tick_id)
        self._intervalo_actual = max(20, int(1000 / self.fps_objetivo))
        self._tick_id = GLib.timeout_add(self._intervalo_actual, self._tick)
        self._ultimo_tick_ms = self._ahora_ms()

    def _tick(self):
        ahora = self._ahora_ms()
        dt = max(1, min(2000, ahora - self._ultimo_tick_ms))
        self._ultimo_tick_ms = ahora

        # Pomodoro (y rutina que le acompaña).
        self.pomodoro.tick(dt)
        # Rutinas.
        self.motor.tick(dt)
        self.motor.mover(dt)
        # Globo de texto.
        self.globo.tick(dt)
        # Movimiento propio de la fase 1 cuando no manda ninguna rutina.
        if not self.motor.activo:
            if self.state == "walk":
                self._tick_walk()
            else:
                self._tick_jump()
        elif self.state == "jump":
            self._tick_jump()

        # Pausa activa (1 vez por segundo).
        if ahora - self._ultimo_pausa_ms >= INTERVALO_MENU_MS:
            self._ultimo_pausa_ms = ahora
            self.pausa.tick()
        # Instantánea para la API HTTP.
        if ahora - self._ultimo_snapshot_ms >= MS_SNAPSHOT_API:
            self._ultimo_snapshot_ms = ahora
            self._refrescar_snapshot()

        if self.backend is not None:
            self.backend.set_input_region(self._rectangulos_entrada())
        self.drawing_area.queue_draw()
        return True

    def _rectangulos_entrada(self):
        """Sprite + globo: lo único que debe recibir el puntero."""
        rects = [self.sprite.rect()]
        globo = self.globo.rect()
        if globo is not None:
            rects.append(globo)
        return rects

    def _tick_walk(self):
        self.sprite.x += SPEED * self.direction

        max_x = self.max_x()
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
        self.jump_t += (self._intervalo_actual / MS_POR_TICK) / JUMP_TICKS
        if self.jump_t >= 1.0:
            self.state = "walk"
            self.sprite.y = self._ground_y()
            self.walk_frame = 0
            self.walk_tick = 0
        else:
            t = self.jump_t
            altura = self.scale * 8
            self.sprite.y = self._ground_y() - altura * math.sin(math.pi * t)

    def _refrescar_menu(self):
        """Mantiene al día el texto del pomodoro en el menú de la bandeja."""
        if self.tray is not None:
            self.tray.refrescar()
        self._refrescar_snapshot()
        return True

    # ------------------------------------------------------- menú / bandeja

    def menu_model(self):
        """Árbol del menú de la bandeja (lo consume tray.Tray)."""
        p = self.pomodoro
        pom_items = [
            {"id": ID_POM_FORMATO_BASE + i, "label": f,
             "checked": p.formato == f}
            for i, f in enumerate(FORMATOS)
        ]
        pom_items += [
            {"id": ID_POM_INICIAR, "label": "Iniciar / reiniciar"},
            {"id": ID_POM_PAUSAR,
             "label": "Reanudar" if p.fase == "parado" and getattr(p, "_guardado", None)
             else "Pausar"},
            {"id": ID_POM_SALTAR, "label": "Saltar de fase"},
        ]
        rutina = self.motor.estado()
        rut_items = [
            {"id": ID_RUT_BASE + i, "label": info["titulo"],
             "checked": self.motor.nombre == nombre}
            for i, (nombre, info) in enumerate(RUTINAS.items())
            if nombre != "descanso_cafe"
        ]
        rut_items.append({"id": ID_RUT_ALEATORIA, "label": "Elegir al azar"})
        pers_items = [
            {"id": ID_PERSONAJE_BASE + i,
             "label": f"{personajes.get_personaje(n).nombre} ({personajes.get_personaje(n).desc})",
             "checked": self.prefs.personaje == n}
            for i, n in enumerate(PERSONAJES)
        ]
        p_act = personajes.get_personaje(self.prefs.personaje)
        return [
            {"id": ID_TOGGLE, "label": "Ocultar" if self.tray.visible else "Mostrar"},
            {"id": ID_POM_ESTADO, "label": p.texto_menu(), "children": pom_items},
            {"id": ID_RUT_ESTADO,
             "label": f"Rutina: {rutina['titulo'] or 'ninguna'}"
                      f"{f' ({rutina['paso']})' if rutina['paso'] else ''}",
             "children": rut_items},
            {"id": ID_PERSONAJE_ESTADO,
             "label": f"Personaje: {p_act.nombre}", "children": pers_items},
            {"id": ID_API,
             "label": f"API local: {'desactivar' if self.api.activo else 'activar'}"},
            {"id": ID_POMODORO_PAUSA,
             "label": f"Pausa activa: {'desactivar' if self.pausa.activo else 'activar'}"},
            {"id": ID_QUIT, "label": "Salir"},
        ]

    def on_menu(self, item_id):
        """Acción de un elemento del menú de la bandeja."""
        # Pomodoro: formatos
        for i, formato in enumerate(FORMATOS):
            if item_id == ID_POM_FORMATO_BASE + i:
                self.pomodoro.formato = formato
                self.prefs.set("formato_pomodoro", formato)
                self.prefs.guardar()
                self._empezar_rutina_de_fase()
                self.on_cambio()
                return
        if item_id == ID_POM_INICIAR:
            self.pomodoro.iniciar()
            self._empezar_rutina_de_fase()
            self.motor.cancelar("pomodoro")
            self.globo.mostrar(f"¡A trabajar! {self.pomodoro.reloj()}", 3000)
            self.on_cambio()
            return
        if item_id == ID_POM_SALTAR:
            self.pomodoro.saltar()
            self._empezar_rutina_de_fase()
            self.on_cambio()
            return
        # Rutinas
        for nombre in RUTINAS:
            if item_id == ID_RUT_BASE + list(RUTINAS).index(nombre):
                if nombre == "descanso_cafe":
                    continue
                self.motor.iniciar(nombre)
                self.on_cambio()
                return
        if item_id == ID_RUT_ALEATORIA:
            self.motor.iniciar(self.motor.elegir())
            self.on_cambio()
            return
        # Personaje
        for i, nombre in enumerate(PERSONAJES):
            if item_id == ID_PERSONAJE_BASE + i:
                self._aplicar_personaje(nombre)
                self.prefs.personaje = nombre
                self.prefs.guardar()
                p = personajes.get_personaje(nombre)
                self.globo.mostrar(f"¡Hola! Soy {p.nombre}", 2500)
                print(f"[mascota] personaje -> {p.nombre} ({p.id})")
                self.on_cambio()
                return
        if item_id == ID_API:
            activa = self.api.alternar()
            self.prefs.set("api_activa", activa)
            self.prefs.guardar()
            self.on_cambio()
            return
        if item_id == ID_POMODORO_PAUSA:
            self.pausa.activo = not self.pausa.activo
            if self.pausa.activo and self.pausa.detector is None:
                self.pausa.detector = self._crear_detector()
            self.prefs.set("pausa_activa", self.pausa.activo)
            self.prefs.guardar()
            self.on_cambio()
            return

    def _crear_detector(self):
        from pausa import crear_detector
        return crear_detector()

    def _empezar_rutina_de_fase(self):
        """Al cambiar de fase del pomodoro, la mascota acompaña."""
        if self.pomodoro.fase == FASE_TRABAJO:
            self.motor.iniciar("echar_codigo")
        elif self.pomodoro.fase == "descanso":
            self.motor.iniciar("descanso_cafe")
            self.globo.mostrar("descanso ☕", 2500)

    # ------------------------------------------------------------- API HTTP

    def estado_actual(self):
        """Instantánea completa (la usan la API y el menú)."""
        estado = {
            "personaje": self.prefs.personaje,
            "dias_uso": self.prefs.dias_uso,
            "backend": self.backend_name,
            "fps": self.fps_objetivo,
            "sprite": {
                "x": round(self.sprite.x, 1),
                "y": round(self.sprite.y, 1),
                "ancho": self.sprite.width,
                "alto": self.sprite.height,
                "color": self.prefs.personaje,
            },
            "rutina": self.motor.estado(),
            "globo": self.globo.texto if self.globo.visible else None,
            "pomodoro": self.pomodoro.estado(),
            "pausa_activa": self.pausa.estado_actual(),
            "api": self.api.estado(),
        }
        return estado

    def estado_api(self):
        """Lo que devuelve GET /estado (lo usa el hilo HTTP)."""
        return dict(self._estado_cache)

    def _refrescar_snapshot(self):
        self._estado_cache = self.estado_actual()

    def accion_api(self, accion, datos):
        """Punto de entrada de la API (lo llama el hilo HTTP)."""
        if accion == "listar_rutinas":
            return {
                "rutinas": [
                    {"nombre": n, "titulo": info["titulo"],
                     "peso": info["peso"]}
                    for n, info in RUTINAS.items()
                ],
                "acciones": ["ir_a", "decir", "cara", "esperar", "objeto",
                             "saltar", "fin"],
            }
        # Validación rápida (aquí no se toca GTK, solo datos).
        if accion in ("aviso", "decir") and not str(datos.get("texto", "")).strip():
            return 400, {"error": "falta 'texto'"}
        if accion == "rutina" and datos.get("nombre") not in RUTINAS:
            return 400, {"error": f"rutina desconocida: {datos.get('nombre')!r}",
                         "rutinas": list(RUTINAS)}
        if accion == "pomodoro" and datos.get("formato") not in (None, *FORMATOS):
            return 400, {"error": f"formato desconocido: {datos.get('formato')!r}",
                         "formatos": list(FORMATOS)}
        if accion == "personaje":
            nombre = str(datos.get("nombre", "")).lower().strip()
            if nombre not in PERSONAJES and nombre not in personajes.ALIAS_LEGACY:
                return 400, {"error": f"personaje desconocido: {nombre!r}",
                             "personajes": list(PERSONAJES)}
        self._cola_api.put((accion, dict(datos or {})))
        GLib.idle_add(self._procesar_cola_api)
        return 202, {"ok": True, "encolado": accion}
    def _procesar_cola_api(self):
        """Ejecuta en el hilo principal lo que llegó por la API."""
        while True:
            try:
                accion, datos = self._cola_api.get_nowait()
            except queue.Empty:
                return False
            try:
                self._aplicar_accion_api(accion, datos)
            except Exception as exc:  # noqa: BLE001
                print(f"[api] error aplicando '{accion}': {exc}")
        return False

    def _aplicar_accion_api(self, accion, datos):
        if accion in ("aviso", "decir"):
            texto = str(datos.get("texto", ""))[:200]
            if not texto:
                return
            ms = int(datos.get("ms") or (1800 if accion == "aviso" else 4000))
            self.globo.mostrar(texto, max(400, min(ms, 30000)))
            print(f"[api] {accion}: {texto}")
        elif accion == "rutina":
            nombre = str(datos.get("nombre", ""))
            if self.motor.iniciar(nombre):
                print(f"[api] rutina '{nombre}'")
            else:
                print(f"[api] rutina desconocida: {nombre!r}")
        elif accion == "pomodoro":
            self._accion_pomodoro(datos)
        elif accion == "personaje":
            nombre = str(datos.get("nombre", "")).lower().strip()
            self._aplicar_personaje(nombre)
            self.prefs.personaje = nombre
            self.prefs.guardar()
            p = personajes.get_personaje(nombre)
            self.globo.mostrar(f"¡Cambiado a {p.nombre}!", 2500)
            print(f"[api] personaje -> '{p.nombre}'")
        self.on_cambio()

    def _accion_pomodoro(self, datos):
        p = self.pomodoro
        accion = str(datos.get("accion", "")).lower()
        formato = datos.get("formato")
        if formato in FORMATOS:
            p.formato = formato
            self.prefs.set("formato_pomodoro", formato)
            self.prefs.guardar()
        if accion in ("iniciar", "start", "reiniciar"):
            p.iniciar()
            self.motor.cancelar("pomodoro")
            self.globo.mostrar(f"¡A trabajar! {p.reloj()}", 3000)
            self._empezar_rutina_de_fase()
        elif accion in ("pausar", "pause"):
            if not p.pausar():
                print("[api] pausar: no estaba en marcha")
        elif accion in ("reanudar", "resume", "continuar"):
            if p.reanudar():
                self._empezar_rutina_de_fase()
        elif accion in ("saltar", "skip"):
            if p.saltar():
                self._empezar_rutina_de_fase()
        elif accion in ("parar", "stop"):
            p.parar()
        else:
            print(f"[api] acción de pomodoro desconocida: {accion!r}")


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
