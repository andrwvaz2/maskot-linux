"""Backend para X11 (también vía XWayland con GDK_BACKEND=x11).

Prepara una ventana sin decoraciones como "dock" y aplica las propiedades EWMH
(_NET_WM_WINDOW_TYPE_DOCK, _NET_WM_STATE_ABOVE/SKIP_TASKBAR/SKIP_PAGER) y el
posicionamiento con ctypes sobre libX11, porque GTK4 ya no expone `set_keep_above`
ni `move()`.

Abrimos nuestra propia conexión X (XOpenDisplay) para estos cambios: los
átomos y propiedades son del servidor, así que funcionan desde otra conexión
del mismo usuario, y evitamos el wrapper `xlib.Display` de PyGObject (que no
expone el puntero crudo para ctypes).

El click-through lo gestiona la clase base mediante `Gdk.Surface.set_input_region`
(que en X11 usa XShape internamente).

NOTA/TODO: `_NET_WM_WINDOW_TYPE_DOCK` en WMs tiling (i3, bspwm) puede reservar
una franja de pantalla (struts). Para una mascota quizá convenga usar
`_NET_WM_WINDOW_TYPE_NOTIFICATION`; está pendiente de verificar en i3/bspwm.
"""

from __future__ import annotations

import ctypes

from gi.repository import Gdk, GdkX11

from backends.base import Backend

# PropModeReplace (0) de Xlib: reemplaza la propiedad.
_PROP_MODE_REPLACE = 0


def _load_xlib():
    """Carga libX11 con ctypes o devuelve None si no está disponible."""
    try:
        xlib = ctypes.CDLL("libX11.so.6")
    except OSError:
        return None

    xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
    xlib.XOpenDisplay.restype = ctypes.c_void_p

    xlib.XCloseDisplay.argtypes = [ctypes.c_void_p]
    xlib.XCloseDisplay.restype = ctypes.c_int

    xlib.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    xlib.XInternAtom.restype = ctypes.c_ulong

    xlib.XChangeProperty.argtypes = [
        ctypes.c_void_p,          # Display*
        ctypes.c_ulong,           # Window
        ctypes.c_ulong,           # property (Atom)
        ctypes.c_ulong,           # type (Atom)
        ctypes.c_int,             # format (8/16/32)
        ctypes.c_int,             # mode
        ctypes.c_void_p,          # data
        ctypes.c_int,             # nelements
    ]
    xlib.XChangeProperty.restype = ctypes.c_int

    xlib.XMoveWindow.argtypes = [
        ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
    ]
    xlib.XMoveWindow.restype = ctypes.c_int

    xlib.XResizeWindow.argtypes = [
        ctypes.c_void_p, ctypes.c_ulong, ctypes.c_uint, ctypes.c_uint,
    ]
    xlib.XResizeWindow.restype = ctypes.c_int

    xlib.XFlush.argtypes = [ctypes.c_void_p]
    xlib.XFlush.restype = ctypes.c_int
    return xlib


class X11Backend(Backend):
    name = "x11"

    def __init__(self, window):
        super().__init__(window)
        self._xlib = _load_xlib()
        self._dpy = None
        self.pending_move = None  # (x, y, width, height) o None

    def _display(self):
        """Abre (una sola vez) nuestra propia conexión X para los cambios."""
        if self._xlib is None:
            return None
        if self._dpy is None:
            self._dpy = self._xlib.XOpenDisplay(None)
            if not self._dpy:
                print("[x11] no se pudo abrir el display X11")
        return self._dpy

    def _xid(self):
        """Devuelve el id de ventana X de la ventana GTK, o None."""
        surface = self.window.get_surface()
        if surface is None:
            return None
        try:
            return int(GdkX11.X11Surface.get_xid(surface))
        except Exception as exc:  # noqa: BLE001 - defensivo
            print(f"[x11] no se pudo obtener el xid: {exc}")
            return None

    def setup(self):
        self.window.set_decorated(False)
        self.window.set_resizable(False)

    def on_mapped(self):
        self._apply_ewmh_properties()
        if self.pending_move is not None:
            self._move_resize(*self.pending_move)

    def _apply_ewmh_properties(self):
        """Aplica _NET_WM_WINDOW_TYPE_DOCK y _NET_WM_STATE (above/skip)."""
        dpy = self._display()
        xid = self._xid()
        if dpy is None or xid is None:
            return
        win = ctypes.c_ulong(xid)

        def atom(name):
            return self._xlib.XInternAtom(dpy, name.encode(), 0)

        atom_type = atom("_NET_WM_WINDOW_TYPE")
        atom_state = atom("_NET_WM_STATE")
        atom_xatom = atom("ATOM")

        # _NET_WM_WINDOW_TYPE = _NET_WM_WINDOW_TYPE_DOCK
        dock = atom("_NET_WM_WINDOW_TYPE_DOCK")
        data = (ctypes.c_ulong * 1)(dock)
        self._xlib.XChangeProperty(dpy, win, atom_type, atom_xatom, 32,
                                   _PROP_MODE_REPLACE, data, 1)

        # _NET_WM_STATE = ABOVE, SKIP_TASKBAR, SKIP_PAGER
        above = atom("_NET_WM_STATE_ABOVE")
        skip_taskbar = atom("_NET_WM_STATE_SKIP_TASKBAR")
        skip_pager = atom("_NET_WM_STATE_SKIP_PAGER")
        data = (ctypes.c_ulong * 3)(above, skip_taskbar, skip_pager)
        self._xlib.XChangeProperty(dpy, win, atom_state, atom_xatom, 32,
                                   _PROP_MODE_REPLACE, data, 3)

        self._xlib.XFlush(dpy)
        print(f"[x11] propiedades EWMH aplicadas a la ventana 0x{xid:x}")

    def _move_resize(self, x, y, width, height):
        """Posiciona y redimensiona la ventana con X11 (GTK4 no lo expone)."""
        dpy = self._display()
        xid = self._xid()
        if dpy is None or xid is None:
            return
        win = ctypes.c_ulong(xid)
        self._xlib.XMoveWindow(dpy, win, int(x), int(y))
        self._xlib.XResizeWindow(dpy, win, int(width), int(height))
        self._xlib.XFlush(dpy)

    def cleanup(self):
        if self._xlib is not None and self._dpy is not None:
            self._xlib.XCloseDisplay(self._dpy)
            self._dpy = None
