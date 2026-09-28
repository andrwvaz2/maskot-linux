#!/usr/bin/env bash
# Verifica las dependencias mínimas y lanza la mascota.
# Uso: ./run.sh [--x11] [--scale N]
set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fail() { echo "ERROR: $*" >&2; exit 1; }
warn() { echo "AVISO: $*" >&2; }

command -v python3 >/dev/null 2>&1 || fail "python3 no está instalado"

# Dependencias Python/GTK4 mínimas.
python3 - <<'PY' || fail "faltan dependencias Python (PyGObject/GTK4/cairo)"
import importlib.util
for mod in ("gi", "cairo"):
    if importlib.util.find_spec(mod) is None:
        raise SystemExit(f"falta el módulo '{mod}'")
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk  # noqa: F401
PY

# Aviso informativo si falta gtk4-layer-shell (solo importa en sesiones Wayland).
layer_shell_ok() {
    python3 - <<'PY'
import importlib.util
if importlib.util.find_spec("gi") is None:
    raise SystemExit(1)
try:
    import gi
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gtk4LayerShell  # noqa: F401
except Exception:
    raise SystemExit(1)
raise SystemExit(0)
PY
}

if layer_shell_ok; then
    echo "gtk4-layer-shell: disponible"
elif [ "${XDG_SESSION_TYPE:-}" = "wayland" ]; then
    # Con --x11 el backend X11 no necesita gtk4-layer-shell: no molestamos.
    _force_x11=0
    for _arg in "$@"; do
        if [ "$_arg" = "--x11" ]; then
            _force_x11=1
        fi
    done
    if [ "$_force_x11" -eq 0 ]; then
        warn "falta gtk4-layer-shell: la mascota NO quedará anclada abajo ni encima."
        warn "  Sin él se usa una ventana normal (sin posición fija) y, en niri,"
        warn "  además toma el foco y se ve como una barra opaca."
        warn "  Instálalo con:"
        warn "    Arch / CachyOS : sudo pacman -S gtk4-layer-shell"
        warn "    Debian/Ubuntu  : sudo apt install libgtk4-layer-shell0"
        warn "    Fedora         : sudo dnf install gtk4-layer-shell"
        warn "  Alternativa: ejecutar con --x11 (ventana X11/XWayland)."
        warn "  Reinstálalo y vuelve a lanzar ./run.sh"
    fi
else
    echo "gtk4-layer-shell: NO disponible (no hace falta en X11)"
fi

# gtk4-layer-shell debe cargarse ANTES que libwayland (orden de enlace). Como
# Python carga GTK (y por tanto libwayland) antes que el typelib, lo resolvemos
# con LD_PRELOAD de forma automática.
for _lib in /usr/lib/libgtk4-layer-shell.so /usr/lib64/libgtk4-layer-shell.so; do
    if [ -e "$_lib" ]; then
        export LD_PRELOAD="${LD_PRELOAD:+$LD_PRELOAD:}$_lib"
        break
    fi
done

exec python3 -u "$DIR/main.py" "$@"
