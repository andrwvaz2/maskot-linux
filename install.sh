#!/usr/bin/env bash
# ==============================================================================
#  👾 MASKOT — Instalador y Configurador de Escritorio / Window Manager
# ==============================================================================
# Soporta: niri, Hyprland, Sway, River, Wayfire, i3, bspwm, GNOME, KDE, XFCE, etc.
# ==============================================================================

set -euo pipefail

# Colores y estilo retro terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Determinar directorio de origen o clonar si se ejecuta vía pipe/curl
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" >/dev/null 2>&1 && pwd || pwd)"

if [[ ! -f "${SCRIPT_DIR}/run.sh" ]]; then
    REPO_URL="https://github.com/andrwvaz2/maskot-linux.git"
    INSTALL_DIR="${HOME}/.local/share/maskot"
    echo -e "${CYAN}▶${NC} No se detectó el código fuente en la carpeta actual."
    echo -e "${CYAN}▶${NC} Descargando Maskot en ${BOLD}${INSTALL_DIR}${NC}..."
    if [[ -d "$INSTALL_DIR" ]]; then
        git -C "$INSTALL_DIR" pull --quiet 2>/dev/null || true
    else
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    fi
    SCRIPT_DIR="$INSTALL_DIR"
fi

BIN_DIR="${HOME}/.local/bin"
APPS_DIR="${HOME}/.local/share/applications"
ICONS_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
AUTOSTART_DIR="${HOME}/.config/autostart"

# Flags por defecto
ARG_WM=""
ARG_AUTOSTART=""
ARG_DEPS=""
ARG_UNINSTALL=0

# ------------------------------------------------------------------------------
# Mensajes de estado y entrada
# ------------------------------------------------------------------------------
log_info()  { echo -e "${CYAN}▶${NC} $*"; }
log_ok()    { echo -e "${GREEN}✔${NC} $*"; }
log_warn()  { echo -e "${YELLOW}▲ AVISO:${NC} $*"; }
log_err()   { echo -e "${RED}✖ ERROR:${NC} $*" >&2; }

prompt_input() {
    local text="$1"
    local def="${2:-}"
    local val=""

    if [ -t 0 ]; then
        read -rp "$text" val
    elif [ -e /dev/tty ]; then
        read -rp "$text" val < /dev/tty 2>/dev/null || val="$def"
    else
        val="$def"
    fi
    echo "${val:-$def}"
}

print_banner() {
    echo -e "${PURPLE}"
    echo "  ╔═══════════════════════════════════════════════════════════╗"
    echo "  ║        👾 M A S K O T — I N S T A L A D O R   v0.2        ║"
    echo "  ║      Configurador Multi-Escritorio y Window Managers      ║"
    echo "  ╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

usage() {
    print_banner
    echo -e "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --wm <entorno>        Fuerza la configuración para un entorno específico:"
    echo "                        [niri, hyprland, sway, i3, bspwm, gnome, kde, xfce, generic]"
    echo "  --deps                Instala dependencias automáticamente con el gestor del sistema"
    echo "  --no-deps             Omite la comprobación/instalación de dependencias del sistema"
    echo "  --autostart           Habilita inicio automático sin preguntar"
    echo "  --no-autostart        Deshabilita inicio automático sin preguntar"
    echo "  --uninstall           Desinstala binarios, accesos directos, iconos y autostart"
    echo "  -h, --help            Muestra esta ayuda"
    echo ""
    exit 0
}

# ------------------------------------------------------------------------------
# Procesar argumentos CLI
# ------------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --wm)
            ARG_WM="${2:-}"
            shift 2
            ;;
        --deps)
            ARG_DEPS="yes"
            shift
            ;;
        --no-deps)
            ARG_DEPS="no"
            shift
            ;;
        --autostart)
            ARG_AUTOSTART="yes"
            shift
            ;;
        --no-autostart)
            ARG_AUTOSTART="no"
            shift
            ;;
        --uninstall)
            ARG_UNINSTALL=1
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_err "Opción desconocida: $1"
            usage
            ;;
    esac
done

# ------------------------------------------------------------------------------
# Desinstalación
# ------------------------------------------------------------------------------
uninstall_maskot() {
    print_banner
    log_info "Desinstalando Maskot del sistema..."

    if [[ -f "${BIN_DIR}/maskot" ]]; then
        rm -f "${BIN_DIR}/maskot"
        log_ok "Binario ${BIN_DIR}/maskot eliminado."
    fi

    if [[ -f "${APPS_DIR}/maskot.desktop" ]]; then
        rm -f "${APPS_DIR}/maskot.desktop"
        log_ok "Lanzador ${APPS_DIR}/maskot.desktop eliminado."
    fi

    if [[ -f "${ICONS_DIR}/maskot.svg" ]]; then
        rm -f "${ICONS_DIR}/maskot.svg"
        log_ok "Icono ${ICONS_DIR}/maskot.svg eliminado."
    fi

    if [[ -f "${AUTOSTART_DIR}/maskot.desktop" ]]; then
        rm -f "${AUTOSTART_DIR}/maskot.desktop"
        log_ok "Inicio automático ${AUTOSTART_DIR}/maskot.desktop eliminado."
    fi

    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "${APPS_DIR}" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
    fi

    echo ""
    log_ok "Maskot ha sido desinstalado de tu cuenta de usuario."
    log_info "Nota: Si se agregaron reglas personalizadas a tu WM (niri, Hyprland, Sway, etc.), puedes retirarlas manualmente de su archivo de configuración."
    exit 0
}

if [[ "${ARG_UNINSTALL}" -eq 1 ]]; then
    uninstall_maskot
fi

# ------------------------------------------------------------------------------
# Detección del Gestor de Paquetes y Dependencias
# ------------------------------------------------------------------------------
detect_pkg_manager() {
    if command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v apt-get >/dev/null 2>&1; then
        echo "apt"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

check_python_deps() {
    python3 - <<'PY' >/dev/null 2>&1
import importlib.util
for mod in ("gi", "cairo"):
    if importlib.util.find_spec(mod) is None:
        raise SystemExit(1)
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk
raise SystemExit(0)
PY
}

check_layer_shell() {
    python3 - <<'PY' >/dev/null 2>&1
try:
    import gi
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gtk4LayerShell
    raise SystemExit(0)
except Exception:
    raise SystemExit(1)
PY
}

install_dependencies() {
    local pm
    pm="$(detect_pkg_manager)"
    local missing_deps=0

    if ! check_python_deps; then
        missing_deps=1
    fi
    if ! check_layer_shell; then
        missing_deps=1
    fi

    if [[ "$missing_deps" -eq 0 ]]; then
        log_ok "Todas las dependencias base (Python 3, GTK4, Cairo, Layer-Shell) están instaladas."
        return 0
    fi

    log_warn "Se detectaron dependencias faltantes en el sistema."

    local cmd=""
    case "$pm" in
        pacman)
            cmd="sudo pacman -S --needed gtk4-layer-shell python-gobject gtk4 python-cairo"
            ;;
        apt)
            cmd="sudo apt update && sudo apt install -y libgtk4-layer-shell0 python3-gi python3-gi-cairo gir1.2-gtk-4.0"
            ;;
        dnf)
            cmd="sudo dnf install -y gtk4-layer-shell python3-gobject gtk4 python3-cairo"
            ;;
        zypper)
            cmd="sudo zypper install -y gtk4-layer-shell python3-gobject gtk4 python3-cairo"
            ;;
        *)
            cmd=""
            ;;
    esac

    if [[ -z "$cmd" ]]; then
        log_warn "No se pudo identificar el gestor de paquetes. Asegúrate de instalar manualmente:"
        echo "  - python3-gobject / pycairo"
        echo "  - gtk4 (4.0+)"
        echo "  - gtk4-layer-shell (para soporte Wayland)"
        return 0
    fi

    local do_install=0
    if [[ "$ARG_DEPS" == "yes" ]]; then
        do_install=1
    elif [[ "$ARG_DEPS" == "no" ]]; then
        log_info "Omitiendo instalación automática de paquetes (--no-deps)."
        return 0
    else
        echo ""
        echo -e "Comando recomendado para tu distribución (${BOLD}${pm}${NC}):"
        echo -e "  ${CYAN}${cmd}${NC}"
        echo ""
        resp="$(prompt_input "¿Deseas ejecutar este comando ahora con sudo? [S/n]: " "s")"
        if [[ "$resp" =~ ^[sSyY]$ ]]; then
            do_install=1
        fi
    fi

    if [[ "$do_install" -eq 1 ]]; then
        log_info "Instalando paquetes del sistema..."
        eval "$cmd"
        log_ok "Paquetes instalados correctamente."
    else
        log_warn "Continuando sin instalar paquetes. Puedes ejecutarlos manualmente si la app falla."
    fi
}

# ------------------------------------------------------------------------------
# Detección del Entorno de Escritorio / Window Manager
# ------------------------------------------------------------------------------
detect_wm() {
    local desktop="${XDG_CURRENT_DESKTOP:-}"
    local session="${DESKTOP_SESSION:-}"

    # 1. niri
    if pidof niri >/dev/null 2>&1 || [[ "$desktop" =~ [Nn]iri ]] || [[ "$session" =~ [Nn]iri ]]; then
        echo "niri"
        return
    fi

    # 2. Hyprland
    if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] || pidof Hyprland >/dev/null 2>&1 || [[ "$desktop" =~ [Hh]yprland ]]; then
        echo "hyprland"
        return
    fi

    # 3. Sway
    if [[ -n "${SWAYSOCK:-}" ]] || pidof sway >/dev/null 2>&1 || [[ "$desktop" =~ [Ss]way ]]; then
        echo "sway"
        return
    fi

    # 4. River
    if [[ -n "${RIVERSOCK:-}" ]] || pidof river >/dev/null 2>&1; then
        echo "river"
        return
    fi

    # 5. i3
    if [[ -n "${I3SOCK:-}" ]] || pidof i3 >/dev/null 2>&1 || [[ "$desktop" =~ [Ii]3 ]]; then
        echo "i3"
        return
    fi

    # 6. bspwm
    if pidof bspwm >/dev/null 2>&1 || [[ "$desktop" =~ [Bb]spwm ]]; then
        echo "bspwm"
        return
    fi

    # 7. GNOME
    if [[ "$desktop" =~ GNOME ]]; then
        echo "gnome"
        return
    fi

    # 8. KDE Plasma
    if [[ "$desktop" =~ KDE ]] || [[ "$desktop" =~ Plasma ]]; then
        echo "kde"
        return
    fi

    # 9. XFCE
    if [[ "$desktop" =~ XFCE ]]; then
        echo "xfce"
        return
    fi

    echo "generic"
}

select_wm_interactive() {
    local detected="$1"
    echo ""
    echo -e "${BOLD}Entornos y Window Managers disponibles para optimizar:${NC}"
    echo "  [1] niri        (Wayland scroll-tiling: regla focus-ring lavanda)"
    echo "  [2] Hyprland    (Wayland dynamic tiling: layerrule & pin)"
    echo "  [3] Sway/River  (Wayland wlroots: reglas floating/sticky)"
    echo "  [4] i3wm        (X11 tiling: floating & sticky)"
    echo "  [5] bspwm       (X11 tiling: regla bspc floating/border)"
    echo "  [6] GNOME       (Wayland / X11: lanzador adaptativo XWayland)"
    echo "  [7] KDE Plasma  (Wayland / X11: soporte KWin nativo)"
    echo "  [8] XFCE / MATE (X11 tradicional: dock EWMH estándar)"
    echo "  [9] Genérico    (Sin reglas especiales)"
    echo ""

    local def_num="9"
    case "$detected" in
        niri) def_num="1" ;;
        hyprland) def_num="2" ;;
        sway|river) def_num="3" ;;
        i3) def_num="4" ;;
        bspwm) def_num="5" ;;
        gnome) def_num="6" ;;
        kde) def_num="7" ;;
        xfce) def_num="8" ;;
    esac

    choice="$(prompt_input "Selecciona tu entorno [1-9, defecto detectado=$def_num]: " "$def_num")"

    case "$choice" in
        1) echo "niri" ;;
        2) echo "hyprland" ;;
        3) echo "sway" ;;
        4) echo "i3" ;;
        5) echo "bspwm" ;;
        6) echo "gnome" ;;
        7) echo "kde" ;;
        8) echo "xfce" ;;
        *) echo "generic" ;;
    esac
}

# ------------------------------------------------------------------------------
# Configuración específica por WM
# ------------------------------------------------------------------------------
setup_niri() {
    log_info "Configurando reglas para niri..."
    local config_file=""

    # Buscar cfg/rules.kdl o config.kdl
    if [[ -f "${HOME}/.config/niri/cfg/rules.kdl" ]]; then
        config_file="${HOME}/.config/niri/cfg/rules.kdl"
    elif [[ -f "${HOME}/.config/niri/config.kdl" ]]; then
        config_file="${HOME}/.config/niri/config.kdl"
    fi

    if [[ -z "$config_file" ]]; then
        mkdir -p "${HOME}/.config/niri"
        config_file="${HOME}/.config/niri/config.kdl"
        touch "$config_file"
    fi

    # Comprobar si ya existe la regla
    if grep -q 'title="\^Mascota\$"' "$config_file" 2>/dev/null || grep -q 'match title="^Mascota$"' "$config_file" 2>/dev/null; then
        log_ok "Regla para Maskot ya presente en $config_file."
    else
        cp "$config_file" "${config_file}.bak"
        cat <<'KDL' >> "$config_file"

// Maskot - Desktop Pet Window Rules (evita focus-ring lavanda y robo de foco)
window-rule {
    match title="^Mascota$"
    open-focused false
    focus-ring { off; }
}
KDL
        log_ok "Regla añadida a $config_file (copia de seguridad en ${config_file}.bak)."
    fi
}

setup_hyprland() {
    log_info "Configurando reglas para Hyprland..."
    local config_file="${HOME}/.config/hypr/hyprland.conf"

    if [[ ! -f "$config_file" ]]; then
        log_warn "No se encontró $config_file. Omitiendo inyección automática."
        return
    fi

    if grep -q 'title:\^(Mascota)\$' "$config_file" 2>/dev/null; then
        log_ok "Reglas para Maskot ya presentes en $config_file."
    else
        cp "$config_file" "${config_file}.bak"
        cat <<'CONF' >> "$config_file"

# --- Maskot - Desktop Pet Rules ---
layerrule = noanim, ^(mascota)$
windowrulev2 = float, title:^(Mascota)$
windowrulev2 = pin, title:^(Mascota)$
windowrulev2 = noblur, title:^(Mascota)$
windowrulev2 = nofocus, title:^(Mascota)$
CONF
        log_ok "Reglas añadidas a $config_file (copia de respaldo: ${config_file}.bak)."
    fi
}

setup_sway() {
    log_info "Configurando reglas para Sway..."
    local config_file="${HOME}/.config/sway/config"

    if [[ ! -f "$config_file" ]]; then
        log_warn "No se encontró $config_file. Omitiendo inyección automática."
        return
    fi

    if grep -q 'title="\^Mascota\$"' "$config_file" 2>/dev/null; then
        log_ok "Regla para Maskot ya presente en $config_file."
    else
        cp "$config_file" "${config_file}.bak"
        cat <<'CONF' >> "$config_file"

# --- Maskot - Desktop Pet Rules ---
for_window [title="^Mascota$"] floating enable, sticky enable, border none, focus_follows_mouse no
CONF
        log_ok "Regla añadida a $config_file."
    fi
}

setup_i3() {
    log_info "Configurando reglas para i3wm..."
    local config_file="${HOME}/.config/i3/config"

    if [[ ! -f "$config_file" ]]; then
        log_warn "No se encontró $config_file. Omitiendo inyección automática."
        return
    fi

    if grep -q 'title="\^Mascota\$"' "$config_file" 2>/dev/null; then
        log_ok "Regla para Maskot ya presente en $config_file."
    else
        cp "$config_file" "${config_file}.bak"
        cat <<'CONF' >> "$config_file"

# --- Maskot - Desktop Pet Rules ---
for_window [title="^Mascota$"] floating enable, sticky enable, border none
CONF
        log_ok "Regla añadida a $config_file."
    fi
}

setup_bspwm() {
    log_info "Configurando reglas para bspwm..."
    local config_file="${HOME}/.config/bspwm/bspwmrc"

    if [[ ! -f "$config_file" ]]; then
        log_warn "No se encontró $config_file. Omitiendo inyección automática."
        return
    fi

    if grep -q 'bspc rule -a Mascota' "$config_file" 2>/dev/null; then
        log_ok "Regla para Maskot ya presente en $config_file."
    else
        cp "$config_file" "${config_file}.bak"
        cat <<'CONF' >> "$config_file"

# --- Maskot - Desktop Pet Rules ---
bspc rule -a Mascota state=floating sticky=on border=off focus=off
CONF
        log_ok "Regla añadida a $config_file."
    fi
}

setup_gnome() {
    log_info "Configuración para GNOME detectada."
    log_info "Mutter (GNOME Wayland) no incluye protocolo layer-shell por defecto."
    log_info "El lanzador de Maskot aplicará automáticamente el modo compatible XWayland (--x11)."
}

setup_kde() {
    log_info "Configuración para KDE Plasma detectada."
    log_ok "KWin Wayland gestiona ventanas layer-shell nativamente sin reglas obligatorias."
}

setup_xfce() {
    log_info "Configuración para XFCE detectada."
    log_ok "XFCE gestiona docks EWMH nativamente."
}

# ------------------------------------------------------------------------------
# Instalación de Componentes del Sistema
# ------------------------------------------------------------------------------
install_system_files() {
    log_info "Instalando lanzador y archivos de integración..."

    mkdir -p "${BIN_DIR}" "${APPS_DIR}" "${ICONS_DIR}" "${AUTOSTART_DIR}"

    # 1. Crear Wrapper ejecutable ~/.local/bin/maskot
    cat <<EOF > "${BIN_DIR}/maskot"
#!/usr/bin/env bash
# Maskot CLI Wrapper generado automáticamente
EXTRA_ARGS=()

# En GNOME Wayland, forzar --x11 para transparencia y anclaje dock
if [ "\${XDG_CURRENT_DESKTOP:-}" = "GNOME" ] && [ "\${XDG_SESSION_TYPE:-}" = "wayland" ]; then
    has_x11=0
    for arg in "\$@"; do
        if [ "\$arg" = "--x11" ]; then
            has_x11=1
        fi
    done
    if [ "\$has_x11" -eq 0 ]; then
        EXTRA_ARGS+=("--x11")
    fi
fi

exec "${SCRIPT_DIR}/run.sh" "\${EXTRA_ARGS[@]}" "\$@"
EOF
    chmod +x "${BIN_DIR}/maskot"
    log_ok "Comando global instalado en: ${BIN_DIR}/maskot"

    # 2. Instalar Icono SVG
    if [[ -f "${SCRIPT_DIR}/assets/maskot.svg" ]]; then
        cp "${SCRIPT_DIR}/assets/maskot.svg" "${ICONS_DIR}/maskot.svg"
        log_ok "Icono instalado en: ${ICONS_DIR}/maskot.svg"
    fi

    # 3. Instalar archivo .desktop
    if [[ -f "${SCRIPT_DIR}/assets/maskot.desktop" ]]; then
        cp "${SCRIPT_DIR}/assets/maskot.desktop" "${APPS_DIR}/maskot.desktop"
        log_ok "Lanzador de aplicaciones instalado en: ${APPS_DIR}/maskot.desktop"
    fi

    # Actualizar bases de datos del sistema
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "${APPS_DIR}" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
    fi

    # Comprobar si ~/.local/bin está en el PATH
    if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
        echo ""
        log_warn "${BIN_DIR} no está actualmente en tu variable PATH."
        echo -e "  Para ejecutar ${BOLD}maskot${NC} desde cualquier terminal, añade a tu ${CYAN}~/.bashrc${NC} o ${CYAN}~/.zshrc${NC}:"
        echo -e "    ${BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    fi
}

# ------------------------------------------------------------------------------
# Configuración de Autostart
# ------------------------------------------------------------------------------
setup_autostart() {
    local enable_auto=0

    if [[ "$ARG_AUTOSTART" == "yes" ]]; then
        enable_auto=1
    elif [[ "$ARG_AUTOSTART" == "no" ]]; then
        enable_auto=0
    else
        echo ""
        resp="$(prompt_input "¿Deseas que Maskot se inicie automáticamente al encender tu PC? [S/n]: " "s")"
        if [[ "$resp" =~ ^[sSyY]$ ]]; then
            enable_auto=1
        fi
    fi

    if [[ "$enable_auto" -eq 1 ]]; then
        cp "${SCRIPT_DIR}/assets/maskot.desktop" "${AUTOSTART_DIR}/maskot.desktop"
        log_ok "Inicio automático configurado en: ${AUTOSTART_DIR}/maskot.desktop"
    else
        if [[ -f "${AUTOSTART_DIR}/maskot.desktop" ]]; then
            rm -f "${AUTOSTART_DIR}/maskot.desktop"
        fi
        log_info "Inicio automático deshabilitado."
    fi
}

# ------------------------------------------------------------------------------
# Flujo Principal
# ------------------------------------------------------------------------------
main() {
    print_banner

    # 1. Comprobar e instalar dependencias
    install_dependencies

    # 2. Determinar entorno
    local target_wm="$ARG_WM"
    if [[ -z "$target_wm" ]]; then
        local detected
        detected="$(detect_wm)"
        log_info "Entorno detectado automáticamente: ${BOLD}${detected}${NC}"
        target_wm="$(select_wm_interactive "$detected")"
    fi

    log_info "Aplicando perfil para: ${BOLD}${target_wm}${NC}"

    case "$target_wm" in
        niri)     setup_niri ;;
        hyprland) setup_hyprland ;;
        sway|river) setup_sway ;;
        i3)       setup_i3 ;;
        bspwm)    setup_bspwm ;;
        gnome)    setup_gnome ;;
        kde)      setup_kde ;;
        xfce)     setup_xfce ;;
        generic)  log_info "Usando configuración genérica." ;;
        *)
            log_warn "Entorno '$target_wm' no reconocido. Usando configuración genérica."
            ;;
    esac

    # 3. Instalar binario wrapper e integración de escritorio
    install_system_files

    # 4. Configurar autostart
    setup_autostart

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}✨ ¡INSTALACIÓN COMPLETADA CON ÉXITO! ✨${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Formas de iniciar Maskot:"
    echo -e "  1. Desde la terminal : ${BOLD}maskot${NC}  (o ./run.sh)"
    echo -e "  2. Con parámetros    : ${BOLD}maskot --scale 8${NC}  (o --x11)"
    echo -e "  3. Desde tu menú     : Busca ${BOLD}Maskot${NC} en tu lanzador de aplicaciones (Rofi, Wofi, GNOME, etc.)"
    echo ""
}

main "$@"
