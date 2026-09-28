"""Pausa activa: detectar inactividad y proponer un estiramiento guiado.

Importante: aquí **solo** se consulta el tiempo de inactividad que publica el
compositor. No se leen teclas, no hay keylogger, no se graba nada; es el mismo
dato que usan los salvapantallas.

Dos formas de obtenerlo:

- Wayland: protocolo `ext-idle-notify-v1`. Se habla directamente con
  `libwayland-client` por ctypes porque no hay binding de Python instalado. El
  aviso de "el usuario lleva X ms quieto" lo emite el compositor.
- X11: extensión `MIT-SCREEN-SAVER` (`XScreenSaverQueryInfo`). Ojo: XWayland no
  expone esa extensión, así que en una sesión Wayland con `--x11` esta vía no
  funciona (se avisa por consola y la pausa activa queda desactivada).

Si no hay ninguna de las dos, la pausa activa se desactiva y se dice por consola
en vez de fingir que funciona.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import subprocess
import sys
import threading
import time

# Tiempo de uso continuo antes de proponer el estiramiento.
MINUTOS_ACTIVIDAD = 50
# Si el usuario lleva este tiempo sin tocar nada, la racha se considera rota.
INACTIVIDAD_ROTA_MS = 60_000
# Cuenta atrás del estiramiento (segundos).
CUENTA_ATRAS = 3
# Duración del estiramiento una vez empezado (segundos; se descuenta 1 por
# consulta, que se hace una vez por segundo).
DURACION_ESTIRAMIENTO_SEG = 6


# ---------------------------------------------------------------------------
# X11: MIT-SCREEN-SAVER
# ---------------------------------------------------------------------------

class _XScreenSaverInfo(ctypes.Structure):
    _fields_ = [
        ("window", ctypes.c_ulong),      # XID
        ("state", ctypes.c_int),         # int
        ("kind", ctypes.c_int),          # int
        ("til_or_since", ctypes.c_ulong),
        ("idle", ctypes.c_ulong),        # ms
        ("event_mask", ctypes.c_ulong),
    ]


class X11Idle:
    """Tiempo de inactividad vía XScreenSaverQueryInfo (X11 real)."""

    def __init__(self):
        self.nombre = "X11/XScreenSaver"
        self.disponible = False
        self.error = None
        self._dpy = None
        self._root = None
        self._query = None
        try:
            self._conectar()
            self.disponible = True
        except Exception as exc:  # noqa: BLE001
            self.error = str(exc)
            print(f"[pausa] inactividad por X no disponible: {exc}")

    def _conectar(self):
        lib = ctypes.CDLL("libX11.so.6")
        lib.XOpenDisplay.argtypes = [ctypes.c_char_p]
        lib.XOpenDisplay.restype = ctypes.c_void_p
        lib.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        lib.XDefaultRootWindow.restype = ctypes.c_ulong
        lib.XQueryExtension.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ]
        lib.XQueryExtension.restype = ctypes.c_int

        dpy = lib.XOpenDisplay(None)
        if not dpy:
            raise OSError("no se pudo abrir el display X11")
        self._dpy = dpy
        self._root = lib.XDefaultRootWindow(dpy)

        presente = ctypes.c_int()
        major = ctypes.c_int()
        minor = ctypes.c_int()
        ok = lib.XQueryExtension(dpy, b"MIT-SCREEN-SAVER",
                                 ctypes.byref(presente), ctypes.byref(major),
                                 ctypes.byref(minor))
        if not ok or not presente.value:
            raise OSError("el servidor X no expone MIT-SCREEN-SAVER "
                          "(normal en XWayland)")

        lib.XScreenSaverQueryInfo.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(_XScreenSaverInfo),
        ]
        lib.XScreenSaverQueryInfo.restype = ctypes.c_int
        self._query = lib.XScreenSaverQueryInfo

    def idle_ms(self):
        if not self.disponible:
            return 0
        info = _XScreenSaverInfo()
        if not self._query(self._dpy, self._root, ctypes.byref(info)):
            return 0
        return int(info.idle)


# ---------------------------------------------------------------------------
# Wayland: ext-idle-notify-v1 con libwayland-client por ctypes
# ---------------------------------------------------------------------------

class _WlMessage(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("signature", ctypes.c_char_p),
        ("types", ctypes.POINTER(ctypes.c_void_p)),
    ]


class _WlInterface(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("version", ctypes.c_int),
        ("method_count", ctypes.c_int),
        ("methods", ctypes.POINTER(_WlMessage)),
        ("event_count", ctypes.c_int),
        ("events", ctypes.POINTER(_WlMessage)),
    ]


class _WlListenerStruct(ctypes.Structure):
    """`struct wl_listener`: un puntero a función + datos."""

    _fields_ = [("notify", ctypes.c_void_p), ("data", ctypes.c_void_p)]


class WaylandIdle:
    """Inactividad vía `ext-idle-notify-v1` sobre una conexión propia.

    Se abre una segunda conexión a libwayland (independiente de la de GTK) para
    no tocar la de GDK. Un hilo bloquea en `wl_display_dispatch()` recibiendo
    eventos; los callbacks solo escriben en un lock, nunca llaman a GTK.

    El marshalling a mano es delicado, así que antes de hacerlo en el proceso de
    la app se ejecuta un auto-test en un subproceso (`pausa.py --selftest`): si no
    termina con 0, la vía se marca como no disponible y no se intenta en el
    proceso principal (así un error de ctypes no tumba la mascota).
    """

    TIMEOUT_SOLICITADO_MS = 60000

    def __init__(self, on_idled=None, on_resumed=None):
        self.nombre = "Wayland/ext-idle-notify-v1"
        self.disponible = False
        self.error = None
        self._dpy = None
        self._thread = None
        self._lock = threading.Lock()
        self._idle_ms = 0
        self._ultimo_idled = 0.0
        self._on_idled = on_idled
        self._on_resumed = on_resumed
        self._refs = []          # evita que el GC recoja los callbacks de C
        self._globals = {}
        try:
            if not self._autotest():
                raise OSError("el auto-test de ext-idle-notify-v1 falló")
            self._conectar()
            self.disponible = True
        except Exception as exc:  # noqa: BLE001
            self.error = str(exc)
            print(f"[pausa] ext-idle-notify-v1 no disponible: {exc}")

    # -- auto-test en subproceso -------------------------------------------

    @staticmethod
    def _autotest():
        try:
            proc = subprocess.run(
                [sys.executable, os.path.abspath(__file__), "--selftest"],
                capture_output=True, timeout=10,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"[pausa] no se pudo lanzar el auto-test: {exc}")
            return False
        if proc.returncode != 0:
            detalle = (proc.stderr or b"").decode(errors="replace").strip()
            print(f"[pausa] auto-test falló (rc={proc.returncode}): {detalle}")
            return False
        return True

    # -- conexión ------------------------------------------------------------

    def _conectar(self):
        wl = ctypes.CDLL(ctypes.util.find_library("wayland-client")
                         or "libwayland-client.so.0")
        wl.wl_display_connect.argtypes = [ctypes.c_char_p]
        wl.wl_display_connect.restype = ctypes.c_void_p
        wl.wl_display_dispatch.argtypes = [ctypes.c_void_p]
        wl.wl_display_dispatch.restype = ctypes.c_int
        wl.wl_display_get_error.argtypes = [ctypes.c_void_p]
        wl.wl_display_get_error.restype = ctypes.c_int
        wl.wl_display_roundtrip.argtypes = [ctypes.c_void_p]
        wl.wl_display_roundtrip.restype = ctypes.c_uint32
        wl.wl_proxy_get_version.argtypes = [ctypes.c_void_p]
        wl.wl_proxy_get_version.restype = ctypes.c_int
        wl.wl_proxy_marshal_flags.restype = ctypes.c_void_p
        wl.wl_proxy_add_listener.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                             ctypes.c_void_p]
        wl.wl_proxy_add_listener.restype = ctypes.c_int
        self._wl = wl

        dpy = wl.wl_display_connect(None)
        if not dpy:
            raise OSError("no se pudo conectar a Wayland")
        self._dpy = dpy
        wl.wl_display_roundtrip(dpy)
        if wl.wl_display_get_error(dpy) != 0:
            raise OSError("error al conectar con Wayland")

        # wl_display y wl_registry: la librería exporta sus interfaces.
        ifac_display = ctypes.cast(wl.wl_display_interface,
                                   ctypes.POINTER(_WlInterface))
        ifac_registry = ctypes.cast(wl.wl_registry_interface,
                                    ctypes.POINTER(_WlInterface))

        # 1) wl_display.get_registry (opcode 1). El new_id va en el parámetro
        #    `interface`; el único vararg es un puntero nulo.
        version_display = wl.wl_proxy_get_version(dpy)
        registry = wl.wl_proxy_marshal_flags(
            dpy, 1, ctypes.byref(ifac_registry.contents), version_display, 0,
            None,
        )
        if not registry:
            raise OSError("no se pudo obtener el wl_registry")
        self._registry = registry

        # 2) Listener del registry: apuntamos los globals que nos interesan.
        GLOBAL_CB = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p,
                                     ctypes.c_uint32, ctypes.c_char_p,
                                     ctypes.c_uint32)

        def _global(_data, _proxy, name, interface, version):
            self._globals[interface.decode(errors="ignore")] = (name, version)

        cb_global = GLOBAL_CB(_global)
        self._refs.append(cb_global)
        reg_listener = (_WlListenerStruct * 2)()   # global + global_remove
        reg_listener[0].notify = ctypes.cast(cb_global, ctypes.c_void_p).value
        wl.wl_proxy_add_listener(registry, ctypes.byref(reg_listener), None)
        self._reg_listener = reg_listener
        wl.wl_display_roundtrip(dpy)

        for necesario in ("ext_idle_notifier_v1", "wl_seat"):
            if necesario not in self._globals:
                raise OSError(f"el compositor no anuncia {necesario}")

        # 3) wl_seat: solo lo usamos como objeto en un request, con nombre y
        #    versión basta como interfaz.
        ifac_seat = _WlInterface(b"wl_seat", 1, 0, None, 0, None)
        self._ifac_seat = ifac_seat
        nombre_seat, ver_seat = self._globals["wl_seat"]
        ver_seat = min(ver_seat, 1)
        seat = wl.wl_proxy_marshal_flags(
            registry, 0, ctypes.byref(ifac_seat), ver_seat, 0,
            nombre_seat, b"wl_seat", ver_seat, None,
        )
        if not seat:
            raise OSError("no se pudo enlazar wl_seat")
        self._seat = seat

        # 4) ext_idle_notifier_v1: request 0 = destroy (""), request 1 =
        #    get_ext_idle_notification (new_id, object seat, uint timeout) = "oun".
        ifac_notifier = _WlInterface(b"ext_idle_notifier_v1", 1, 2, None, 0,
                                     None)
        msgs = (_WlMessage * 2)(
            _WlMessage(b"destroy", b"", None),
            _WlMessage(b"get_ext_idle_notification", b"oun", None),
        )
        ifac_notifier.methods = msgs
        self._ifac_notifier = ifac_notifier
        self._msgs = msgs

        nombre_notif, ver_notif = self._globals["ext_idle_notifier_v1"]
        ver_notif = min(ver_notif, 1)
        notifier = wl.wl_proxy_marshal_flags(
            registry, 0, ctypes.byref(ifac_notifier), ver_notif, 0,
            nombre_notif, b"ext_idle_notifier_v1", ver_notif, None,
        )
        if not notifier:
            raise OSError("no se pudo enlazar ext_idle_notifier_v1")
        if wl.wl_display_get_error(dpy) != 0:
            raise OSError("error del servidor al enlazar el notificador")
        self._notifier = notifier

        # 5) get_ext_idle_notification(id, seat, timeout)
        ifac_notif = _WlInterface(b"ext_idle_notification_v1", 1, 0, None, 0,
                                  None)
        self._ifac_notif = ifac_notif
        notif = wl.wl_proxy_marshal_flags(
            notifier, 1, ctypes.byref(ifac_notif), 1, 0,
            seat, self.TIMEOUT_SOLICITADO_MS, None,
        )
        if not notif:
            raise OSError("no se pudo pedir la notificación de inactividad")
        if wl.wl_display_get_error(dpy) != 0:
            raise OSError("error del servidor al pedir la notificación")

        # 6) Listener de ext_idle_notification_v1 (idled, resumed)
        IDLED_CB = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p,
                                    ctypes.c_uint32)
        RESUMED_CB = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)

        def _idled(_data, _proxy, timeout_ms):
            with self._lock:
                self._idle_ms = int(timeout_ms)
                self._ultimo_idled = time.monotonic()
            if self._on_idled:
                self._on_idled(int(timeout_ms))

        def _resumed(_data, _proxy):
            with self._lock:
                self._idle_ms = 0
            if self._on_resumed:
                self._on_resumed()

        cb_idled = IDLED_CB(_idled)
        cb_resumed = RESUMED_CB(_resumed)
        self._refs += [cb_idled, cb_resumed]
        notif_listener = (_WlListenerStruct * 2)()
        notif_listener[0].notify = ctypes.cast(cb_idled, ctypes.c_void_p).value
        notif_listener[1].notify = ctypes.cast(cb_resumed,
                                               ctypes.c_void_p).value
        self._notif_listener = notif_listener
        wl.wl_proxy_add_listener(notif, ctypes.byref(notif_listener), None)
        self._notif = notif
        wl.wl_display_roundtrip(dpy)
        if wl.wl_display_get_error(dpy) != 0:
            raise OSError("error del servidor tras registrar el listener")

        # 7) Hilo que lee eventos (bloquea; no es el hilo de GTK).
        self._thread = threading.Thread(target=self._bucle, daemon=True,
                                        name="idle-notify")
        self._thread.start()

    def _bucle(self):
        while self._dpy:
            try:
                if self._wl.wl_display_dispatch(self._dpy) < 0:
                    break
            except Exception:  # noqa: BLE001
                break

    # -- consulta ------------------------------------------------------------

    def idle_ms(self):
        if not self.disponible:
            return 0
        with self._lock:
            base = self._idle_ms
            ultimo = self._ultimo_idled
        if base <= 0:
            return 0
        # ext-idle-notify-v1 no manda eventos periódicos: sumamos el tiempo
        # transcurrido desde el último "idled" mientras no haya "resumed".
        return int(base + max(0.0, (time.monotonic() - ultimo) * 1000))

    def parar(self):
        self._dpy = None


# ---------------------------------------------------------------------------

def crear_detector():
    """Devuelve el mejor detector de inactividad disponible, o None."""
    sesion = os.environ.get("XDG_SESSION_TYPE", "").lower()
    gdk = os.environ.get("GDK_BACKEND", "").lower()

    if gdk == "x11" or sesion == "x11":
        det = X11Idle()
        return det if det.disponible else None

    if sesion == "wayland":
        det = WaylandIdle()
        return det if det.disponible else None

    det = X11Idle()
    return det if det.disponible else None


class PausaActiva:
    """Propone un estiramiento guiado tras 50 min de uso continuo."""

    def __init__(self, pet, activo=True, minutos=MINUTOS_ACTIVIDAD):
        self.pet = pet
        self.activo = activo
        self.minutos = minutos
        self.detector = crear_detector() if activo else None
        self.estado = "vigilando" if self.detector else "sin detector"
        self.cuenta_atras = 0
        self._ms_cuenta = 0
        self._seg_estiramiento = 0
        self._inicio_racha = time.monotonic()
        self._idle_actual = 0
        if activo and self.detector is None:
            self.activo = False
            print("[pausa] no hay forma de consultar la inactividad "
                  "(ni ext-idle-notify-v1 ni MIT-SCREEN-SAVER); "
                  "la pausa activa queda desactivada")

    # -- ciclo ---------------------------------------------------------------

    def tick(self):
        if not self.activo or self.detector is None:
            return
        ahora = time.monotonic()
        self._idle_actual = self.detector.idle_ms()

        # El usuario se va (>= 1 min): la racha se rompe y se cancela lo que
        # estuviera en marcha. Merece la pena: si sigue delante, el estiramiento
        # se le va a hacer igual (para eso se propone).
        if self._idle_actual >= INACTIVIDAD_ROTA_MS:
            if self.estado in ("cuenta_atras", "estirando"):
                self._fin("usuario ausente")
            self._inicio_racha = ahora
            return

        if self.estado == "vigilando":
            # Ojo: mientras haya actividad (incluso 0 ms de inactividad) el
            # contador NO se reinicia; solo se reinicia si el usuario se va.
            if (ahora - self._inicio_racha) * 1000 >= self.minutos * 60_000:
                self._iniciar_cuenta_atras()

        elif self.estado == "cuenta_atras":
            self._ms_cuenta -= 1
            if self._ms_cuenta <= 0:
                self._iniciar_estiramiento()
            else:
                self.cuenta_atras = self._ms_cuenta
                self.pet.globo.mostrar(f"Estiramiento en {self._ms_cuenta}…",
                                       900)

        elif self.estado == "estirando":
            self._seg_estiramiento -= 1
            if self._seg_estiramiento <= 0:
                self._fin("estiramiento terminado")

    # -- fases ---------------------------------------------------------------

    def _iniciar_cuenta_atras(self):
        self.estado = "cuenta_atras"
        self._ms_cuenta = CUENTA_ATRAS
        self.cuenta_atras = CUENTA_ATRAS
        self.pet.cancelar_rutina("pausa activa")
        self.pet.globo.mostrar(
            f"Llevas {self.minutos} min seguidos. Estírate en {CUENTA_ATRAS}…",
            1200)
        print(f"[pausa] {self.minutos} min de uso continuo: estiramiento guiado")
        self.pet.on_cambio()

    def _iniciar_estiramiento(self):
        self.estado = "estirando"
        self._seg_estiramiento = DURACION_ESTIRAMIENTO_SEG
        self.cuenta_atras = 0
        self.pet.globo.mostrar("Estiramos un poco: brazos arriba", 4000)
        self.pet.poner_pose("estirar")
        print("[pausa] estiramiento en curso")
        self.pet.on_cambio()

    def _fin(self, motivo):
        self.estado = "vigilando"
        self.cuenta_atras = 0
        self._inicio_racha = time.monotonic()
        self.pet.poner_pose(None)
        print(f"[pausa] fin de la pausa activa ({motivo})")
        self.pet.on_cambio()

    # -- información ---------------------------------------------------------

    def estado_actual(self):
        return {
            "activo": self.activo,
            "estado": self.estado,
            "minutos": self.minutos,
            "cuenta_atras": self.cuenta_atras,
            "idle_ms": int(self._idle_actual),
            "detector": getattr(self.detector, "nombre", None),
        }


# ---------------------------------------------------------------------------
# Auto-test: `python3 pausa.py --selftest`
# Enlaza ext-idle-notify-v1 en un proceso aparte y sale con 0 si todo va bien.
# ---------------------------------------------------------------------------

def _selftest():
    if os.environ.get("XDG_SESSION_TYPE", "").lower() != "wayland":
        print("no es una sesión Wayland", file=sys.stderr)
        return 2
    det = WaylandIdle.__new__(WaylandIdle)
    det.nombre = "selftest"
    det.disponible = True
    det.error = None
    det._dpy = None
    det._thread = None
    det._lock = threading.Lock()
    det._idle_ms = 0
    det._ultimo_idled = 0.0
    det._on_idled = None
    det._on_resumed = None
    det._refs = []
    det._globals = {}
    det._conectar()
    if not det._dpy or not getattr(det, "_notif", None):
        print("no se pudo enlazar la notificación", file=sys.stderr)
        return 1
    print("ext-idle-notify-v1 enlazado correctamente")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print("pausa.py: usa --selftest para comprobar ext-idle-notify-v1")
