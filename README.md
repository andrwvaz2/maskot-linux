# Mascota de escritorio en pixel art (prototipo)

Prototipo mínimo de mascota de escritorio para Linux. **Su único objetivo es
validar la parte difícil**: una ventana flotante *transparente* con
*click-through* (el puntero atraviesa la ventana salvo encima del sprite) que
funcione en distintos escritorios.

Todo lo demás (Pomodoro, APIs, selectores de sprite…) está fuera del alcance.

## Requisitos

- Python 3 (probado con 3.14)
- PyGObject con GTK 4 (probado con 4.22)
- pycairo
- Para Wayland: `gtk4-layer-shell` (protocolo `zwlr_layer_shell_v1`)

```bash
# Arch / CachyOS  (gtk4-layer-shell es lo importante para Wayland)
sudo pacman -S gtk4-layer-shell
sudo pacman -S python-gobject gtk4 python-cairo   # resto de dependencias

# Debian / Ubuntu
sudo apt install libgtk4-layer-shell0 python3-gi python3-gi-cairo gir1.2-gtk-4.0

# Fedora
sudo dnf install gtk4-layer-shell python3-gobject gtk4 python3-cairo
```

Comprueba lo instalado con:

```bash
pacman -Q gtk4-layer-shell    # Arch/CachyOS
```

Si `run.sh` detecta que falta en una sesión Wayland, avisa con el comando
exacto para tu distro y recuerda que la mascota quedará sin anclar.

> En sesiones **X11** no hace falta `gtk4-layer-shell`: el backend X11 usa solo
> libX11 (vía ctypes) y GDK.

## Ejecución

```bash
./run.sh              # elige el backend solo
./run.sh --x11        # fuerza X11/XWayland
./run.sh --scale 8    # sprite a 8x (por defecto 4 => 64 px)
```

`run.sh` comprueba dependencias, avisa si falta `gtk4-layer-shell` y, si la
librería está en `/usr/lib`, la precarga con `LD_PRELOAD` (ver “Carga de
gtk4-layer-shell” más abajo). También puedes lanzarlo a mano:

```bash
python3 main.py [--x11] [--scale N]
```

> `--x11` relanza el proceso con `GDK_BACKEND=x11`: GDK lee esa variable al
> abrir el display, y para entonces GTK ya está cargado, así que no basta con
> asignarla dentro del programa.

## Qué hace

| Pieza | Responsabilidad |
|---|---|
| `main.py` | Selección de backend, ventana GTK4, animación a 20 FPS, clic → salto |
| `backends/base.py` | Click-through con `Gdk.Surface.set_input_region` (compartido a ambos backends) |
| `backends/wayland.py` | Layer-shell: capa OVERLAY, anclada abajo/izq/der, teclado NONE |
| `backends/x11.py` | Propiedades EWMH (`_NET_WM_WINDOW_TYPE_DOCK`, `ABOVE`, `SKIP_TASKBAR`), posicionado con `XMoveWindow` |
| `sprite.py` | Frames 16×16 dibujados a mano, escala x4, 4 colores de cuerpo |
| `tray.py` | Bandeja StatusNotifierItem por DBus (Ocultar/Mostrar, Salir) sin libayatana-appindicator |
| `run.sh` | Comprobación de dependencias y arranque |

Comportamiento: la mascota camina de lado a lado rebotando en los bordes;
al hacer clic **salta** y, al aterrizar, cambia de color de cuerpo. El menú de
bandeja la oculta o cierra la app.

El click-through se actualiza **cada tick** con la posición exacta del sprite,
así que el puntero atraviesa toda la ventana excepto los 64×64 px del cuerpo.

## Compatibilidad (qué se verificó y qué no)

Entorno de prueba: **CachyOS + niri (Wayland) + XWayland**.

| Camino | Estado | Cómo se comprobó |
|---|---|---|
| Wayland + layer-shell (recomendado) | ✅ verificado | Capa `mascota` en Overlay/keyboard None; `wl_surface.set_input_region` con `wl_region.add(x, 32, 64, 64)` actualizándose; captura con el sprite visible **y el contenido de atrás viéndose a través** |
| Wayland sin layer-shell (fallback) | ✅ verificado | Aviso por consola; la ventana normal igual recibe `wl_region.add(...)` + `set_input_region` (click-through a nivel de protocolo) |
| X11 / XWayland | ✅ verificado | Shape de entrada = 1 rect justo sobre el sprite; clic real inyectado con XTest → el salto se ejecutó (la región subió de 32 a 0 px); EWMH correcto |
| Bandeja SNI | ✅ verificado | `GetAll` devuelve 8 propiedades, `GetLayout` devuelve “Ocultar”/“Salir”, el clic en “Salir” cierra la app |
| CPU | ✅ verificado | 0–1 % con la animación a 20 FPS (ambos backends) |
| Xorg real (no XWayland) | ❌ no probado | Solo hay sesión Wayland en esta máquina |
| GNOME/KDE Wayland (sin `zwlr_layer_shell`) | ❌ no probado | Sin layer-shell el backend avisa y sigue con ventana normal |
| i3 / bspwm / Openbox | ❌ no probado | Ver limitación de `struts` más abajo |
| Clic real sobre la mascota en Wayland | ⚠️ parcial | Verificado a nivel de protocolo Wayland; no hubo herramienta para inyectar puntero (`wtype`/`ydotool` no están instaladas) |
| Posición “abajo de todo” en X11 | ⚠️ parcial | Funciona con un WM X11 clásico; **en XWayland+niri `XMoveWindow` es ignorado** |

## Limitaciones conocidas

1. **niri: una ventana *toplevel* enfocada se rellena de lavanda.**
   Cuando niri enfoca una ventana normal (X11 **o** Wayland sin layer-shell)
   dibuja su efecto de fondo (focus-ring con degradado `#9ccbfb → #d4bee6`, de
   la paleta del wallpaper) *detrás* de la ventana. Como la ventana es
   transparente, ese relleno se ve entero: se comprobó tanto con el backend
   X11 (barra de 1920×100) como con el fallback Wayland (ventana flotante de
   200×100). Se comprobó que **sin foco la ventana es transparente de verdad**
   (se ve el wallpaper a través) y que la **layer-surface con `keyboard NONE`
   nunca toma foco** → transparencia correcta.

   **Ya está resuelto en la configuración de niri de esta máquina.** En
   `~/.config/niri/cfg/rules.kdl` (copia de seguridad en `rules.kdl.bak`):

   ```kdl
   window-rule {
       match title="^Mascota$"
       open-focused false
       focus-ring { off; }
   }
   ```

   El título que usa la app es exactamente `Mascota` (`main.py`, `set_title`),
   así que la regla solo afecta a la mascota. Comprobado: con la regla la
   ventana aparece con `is_focused = False` y el foco se queda en la ventana
   anterior (sin barra lavanda). Ojo al punto y coma: `focus-ring { off; }`, no
   `focus-ring { off }` (KDL lo rechaza).

   *Contrapartida:* en niri la ventana con `--x11` es una *tile* más del layout
   y, al no tomar el foco, niri no desplaza la vista: puede quedar fuera de
   pantalla. En ese caso usa la ruta Wayland con layer-shell, que no le afecta
   (las layer-surfaces no pasan por estas reglas de ventana).
2. **XWayland ignora `XMoveWindow`.** La ventana X11 queda donde la coloque el
   compositor (niri la hace *tile*), no abajo del todo. En Xorg con un WM
   clásico sí funcionaría. Es la razón principal por la que en Wayland se usa
   layer-shell y no esta ruta.
3. **`_NET_WM_WINDOW_TYPE_DOCK` puede reservar struts** en i3/bspwm y dejar
   una franja muerta al final de la pantalla. Está pendiente de probar; si
   pasa, cambiar a `_NET_WM_WINDOW_TYPE_NOTIFICATION` en
   `backends/x11.py`.
4. **Carga de `gtk4-layer-shell`.** Debe cargarse *antes* que `libwayland`
   (es el orden de enlace de la librería). Si no, `is_supported()` devuelve
   `False` y la app cae al fallback. `run.sh` lo resuelve con `LD_PRELOAD`
   cuando la librería está en `/usr/lib` o `/usr/lib64`.
5. **Bandeja sin libayatana-appindicator.** Esa librería es de GTK3 y no
   convive con GTK4 en el mismo proceso (PyGObject no carga dos versiones del
   namespace `Gtk`), así que el protocolo StatusNotifierItem se habla
   directamente por DBus con Gio.
6. **`Gtk.Application` se descartó a propósito**: en XWayland su arranque
   podía bloquearse en la carga del tema de iconos. Se usa `GLib.MainLoop`.
7. **Posicionamiento de monitores:** GTK4 no expone “monitor primario”
   (`Gdk.Monitor` no tiene `is_primary()`), se usa el primero de la lista.
8. **El fallback Wayland es una ventana flotante de 200×100.** Sin
   layer-shell la app pide un ancho “natural” (0) y GTK calcula 200 px; niri
   la muestra flotando en mitad de pantalla (vista en `(860, 515)`). Sirve
   para comprobar el click-through, pero para tener la mascota abajo del todo
   hace falta layer-shell (Wayland) o `--x11` (X11 clásico).

## Nota sobre el entorno de esta prueba

Al principio esta máquina no tenía `sudo` disponible, así que
`gtk4-layer-shell` no se pudo instalar con el gestor de paquetes y la ruta
Wayland se verificó extrayendo el paquete a mano en `/tmp` y lanzando con
`GI_TYPELIB_PATH` / `LD_LIBRARY_PATH` / `LD_PRELOAD`. Después se instaló el
paquete (`gtk4-layer-shell 1.3.0-1.1`) y la ruta Wayland se volvió a comprobar
con la librería del sistema, sin esas variables:

```console
$ ./run.sh
gtk4-layer-shell: disponible
[wayland] layer-shell OK: capa OVERLAY, anclada abajo/izq/der, keyboard NONE
```

## Estructura

```
mascota/
├── main.py           # app, animación y detección de backend
├── sprite.py         # frames pixel-art 16x16 y paletas
├── tray.py           # bandeja StatusNotifierItem por DBus
├── run.sh            # lanzador con comprobaciones
└── backends/
    ├── __init__.py
    ├── base.py       # set_input_region() vía GDK (X11 y Wayland)
    ├── wayland.py    # gtk4-layer-shell + fallback
    └── x11.py        # EWMH + XMoveWindow con ctypes
```
