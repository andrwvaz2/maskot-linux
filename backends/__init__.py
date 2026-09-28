"""Backends de ventana (X11 y Wayland)."""

from backends.x11 import X11Backend
from backends.wayland import WaylandBackend

__all__ = ["X11Backend", "WaylandBackend"]
