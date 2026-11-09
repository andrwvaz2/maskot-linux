#!/usr/bin/env bash
# Verifica las dependencias mínimas y lanza la mascota.
# Uso: ./run.sh [--x11] [--scale N] [--monitor NOMBRE|ÍNDICE] [--list-monitores]
#
# En la ruta Wayland, gtk4-layer-shell debe cargarse ANTES que libwayland (es el
# orden de enlace de la librería: si se carga después, `is_supported()` devuelve
# False y la mascota cae al fallback sin anclar). Como aquí se carga GTK —y con
# él libwayland— antes que el typelib, lo resolvemos con LD_PRELOAD, y la ruta
# de la librería se busca en vez de suponerla (cambia según la distro).
set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fail() { echo "ERROR: $*" >&2; exit 1; }
warn() { echo "AVISO: $*" >&2; }

command -v python3 >/dev/null 2>&1 || fail "python3 no está instalado"

# --- ¿Han pedido el backend X11 explícitamente? ------------------------------
_force_x11=0
for _arg in "$@"; do
    if [ "$_arg" = "--x11" ]; then
        _force_x11=1
    fi
done

# --- Dependencias Python/GTK4 mínimas ----------------------------------------
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

# --- gtk4-layer-shell: ¿está el typelib? -------------------------------------
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

# --- Buscar la librería compartida ------------------------------------------
# La ruta NO es la misma en todas las distros:
#   Arch/CachyOS -> /usr/lib/libgtk4-layer-shell.so
#   Fedora       -> /usr/lib64/libgtk4-layer-shell.so
#   Debian/Ubuntu-> /usr/lib/x86_64-linux-gnu/libgtk4-layer-shell.so.0 (multiarch)
# Por eso se pregunta primero a ldconfig (dice la ruta real de la caché), luego
# se buscan las rutas habituales con find y, en último caso, se prueban una a
# una. Se puede forzar con MASKOT_LAYER_SHELL_LIB=/ruta/exacta.
LIB_LAYER_SHELL=""

buscar_lib_layer_shell() {
    local cand

    # 0) El usuario puede fijar la ruta (instalaciones fuera del sistema).
    if [ -n "${MASKOT_LAYER_SHELL_LIB:-}" ]; then
        if [ -e "$MASKOT_LAYER_SHELL_LIB" ]; then
            LIB_LAYER_SHELL="$MASKOT_LAYER_SHELL_LIB"
            return 0
        fi
        return 1
    fi

    # 1) ldconfig: la ruta que el cargador dynamic ya tiene en su caché.
    if command -v ldconfig >/dev/null 2>&1; then
        # Se prefiere el .so sin versión; si no, el soname .so.0.
        cand="$(ldconfig -p 2>/dev/null \
                | awk '/libgtk4-layer-shell\.so( |$)/ {print $NF; salida=1} END {}' \
                | head -n 1)"
        if [ -n "$cand" ] && [ -e "$cand" ]; then
            LIB_LAYER_SHELL="$cand"
            return 0
        fi
        cand="$(ldconfig -p 2>/dev/null \
                | awk '/libgtk4-layer-shell\.so\.0/ {print $NF}' | head -n 1)"
        if [ -n "$cand" ] && [ -e "$cand" ]; then
            LIB_LAYER_SHELL="$cand"
            return 0
        fi
    fi

    # 2) find en las rutas habituales de cada distro (incluye multiarch).
    local dirs="/usr/lib /usr/lib64 /lib /lib64 /usr/local/lib"
    if command -v find >/dev/null 2>&1; then
        cand="$(find $dirs /usr/lib/*-linux-gnu -maxdepth 1 \
                -name 'libgtk4-layer-shell.so' 2>/dev/null | head -n 1)"
        if [ -n "$cand" ] && [ -e "$cand" ]; then
            LIB_LAYER_SHELL="$cand"
            return 0
        fi
        cand="$(find $dirs /usr/lib/*-linux-gnu -maxdepth 1 \
                -name 'libgtk4-layer-shell.so.0' 2>/dev/null | head -n 1)"
        if [ -n "$cand" ] && [ -e "$cand" ]; then
            LIB_LAYER_SHELL="$cand"
            return 0
        fi
    fi

    # 3) Rutas conocidas, una a una.
    for cand in /usr/lib/libgtk4-layer-shell.so \
                /usr/lib64/libgtk4-layer-shell.so \
                /lib/libgtk4-layer-shell.so \
                /lib64/libgtk4-layer-shell.so \
                /usr/lib/*-linux-gnu/libgtk4-layer-shell.so \
                /usr/lib/*-linux-gnu/libgtk4-layer-shell.so.0 \
                /usr/local/lib/libgtk4-layer-shell.so; do
        if [ -e "$cand" ]; then
            LIB_LAYER_SHELL="$cand"
            return 0
        fi
    done

    return 1
}

if [ "${XDG_SESSION_TYPE:-}" = "wayland" ] && [ "$_force_x11" -eq 0 ]; then
    # Ruta Wayland: hace falta gtk4-layer-shell para anclar abajo/encima.
    if layer_shell_ok; then
        if buscar_lib_layer_shell; then
            export LD_PRELOAD="${LD_PRELOAD:+$LD_PRELOAD:}$LIB_LAYER_SHELL"
            echo "gtk4-layer-shell: disponible (precargada: $LIB_LAYER_SHELL)"
        else
            warn "gtk4-layer-shell está instalada pero no se encontró la librería"
            warn "  para precargarla; si la mascota aparece sin anclar, fija la ruta:"
            warn "    MASKOT_LAYER_SHELL_LIB=/ruta/a/libgtk4-layer-shell.so ./run.sh"
        fi
    else
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
    # Sesión X11, o --x11 pedido: gtk4-layer-shell no se usa.
    echo "gtk4-layer-shell: no necesaria (ruta X11)"
fi

exec python3 -u "$DIR/main.py" "$@"