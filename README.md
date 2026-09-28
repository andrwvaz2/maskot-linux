# Mascota de escritorio en pixel art (prototipo)

Mascota de escritorio para Linux escrita en Python + GTK4. Prototipo en dos
fases:

- **Fase 1 — la parte difícil**: ventana flotante, *transparente* y con
  *click-through* (el puntero atraviesa la ventana salvo encima del sprite y
  del globo de texto), funcionando en distintos escritorios.
- **Fase 2 — comportamiento**: rutinas, globo de texto, pomodoro, pausa activa,
  API HTTP local y preferencias.

Fuera de alcance: Pomodoro avanzado, integraciones externas, etc. (el pomodoro
es funcional, pero es un temporizador simple).

> ⚠️ **La pausa activa está desactivada por defecto en Wayland.** El protocolo
> `ext-idle-notify-v1` hay que hablarlo a mano con ctypes (no hay binding de
> Python instalado) y en libwayland 1.26 eso provoca un **fallo de
> segmentación**. La app lo detecta con un auto-test en subproceso y avisa por
> consola en vez de romperse. Detalle, comando para reproducirlo y lo que se
> investigó: [sección dedicada](#por-qu%C3%A9-la-pausa-activa-est%C3%A1-desactivada-en-wayland).
> Si instalas un binding real de Wayland, la función se activa sola al arrancar.

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
| `main.py` | Coordinación: backend, bucle de animación, dibujo, menú, API |
| `rutinas.py` | Motor de rutinas y las 5 rutinas (pasear, siesta, leer en la banca, echar código, descanso con café) |
| `objetos.py` | Objetos pixel-art (banca, libro, taza, portátil) |
| `globo.py` | Globo de texto con Cairo (tipografía "toy", sin Pango) |
| `pomodoro.py` | Temporizador 25/5, 45/10 y 50/10 |
| `pausa.py` | Detección de inactividad y estiramiento guiado |
| `api.py` | API HTTP en 127.0.0.1 (apagada por defecto) |
| `preferencias.py` | `~/.config/mascota/prefs.json` (personaje, días de uso…) |
| `backends/base.py` | Click-through con `Gdk.Surface.set_input_region` |
| `backends/wayland.py` | Layer-shell: capa OVERLAY, anclada abajo/izq/der, teclado NONE |
| `backends/x11.py` | Propiedades EWMH y posicionado con `XMoveWindow` |
| `sprite.py` | Frames 16×16, paletas y poses/caras |
| `tray.py` | Bandeja StatusNotifierItem por DBus, con submenús |

### Rutinas

Cada rutina es una lista de acciones y el motor las ejecuta en secuencia sobre
el sprite. Acciones disponibles:

| Acción | Qué hace |
|---|---|
| `ir_a(x)` | Camina hasta la posición `x` (`None` = al azar) |
| `decir(texto, ms)` | Muestra un texto en el globo |
| `cara(nombre, ms)` | Expresión: `feliz`, `cansado`, `pensar` |
| `esperar(ms, pose=…)` | Se queda quieto; `pose` puede ser `siesta`, `leer`, `codigo` |
| `objeto(nombre, x=…)` | Pone/quita un objeto (`banca`, `libro`, `taza`, `portatil`) |
| `saltar()` | Da un salto |
| `fin()` | Termina |

Rutinas incluidas: **pasear**, **siesta**, **leer en la banca**,
**echar código** y **descanso_cafe** (esta última la usa el pomodoro en los
descansos). Cada 20–40 s se elige una al azar con pesos que favorecen las
tranquilas (siesta peso 3, leer y pasear 2, código 1). Durante un pomodoro la
elección se guía por la fase.

Un clic del usuario cancela la rutina y hace saltar a la mascota.

### Globo de texto

Se dibuja con Cairo encima del sprite, con rabito que apunta a él, sombra y
desvanecido al final. **El rectángulo del globo se une al del sprite en la
región de entrada**, así que el texto es interactivo y el resto de la ventana
sigue siendo click-through.

### Pomodoro

Formatos **25/5**, **45/10** y **50/10**, desde el menú de la bandeja. El
tiempo restante aparece en el propio rótulo del menú (“Pomodoro trabajo: 24:31”)
y en el tooltip del icono de bandeja. Al cambiar de fase la mascota acompaña:
en **trabajo** programa o lee, en **descanso** se toma un café.

### Pausa activa

Tras **50 minutos de uso continuo** propone un estiramiento guiado con cuenta
atrás (3, 2, 1) y luego la pose de estiramiento durante 6 s. Si el usuario se
va (≥ 1 min de inactividad) la racha se reinicia y se cancela.

Detecta la inactividad **solo** con el dato que publica el compositor; no lee
teclas ni registra nada:

- **Wayland**: protocolo `ext-idle-notify-v1` hablado con `libwayland-client`
  por ctypes (no hay binding de Python instalado), con un **auto-test en
  subproceso** para no arriesgar el proceso principal.
- **X11**: extensión `MIT-SCREEN-SAVER`.

> **En esta máquina no se pudo verificar ninguna de las dos** (ver “Lo que no
> pude verificar”): XWayland no expone `MIT-SCREEN-SAVER` y el enlace a
> `ext-idle-notify-v1` por ctypes provoca un fallo de segmentación. El
> auto-test lo detecta y la pausa activa queda **desactivada con un aviso por
> consola**, sin romper nada. La máquina de estados sí está probada con un
> detector simulado.

### ⚠️ Por qué la pausa activa está desactivada en Wayland

Este es el punto más incómodo del prototipo, así que va aquí y no escondido en
las limitaciones. **En Wayland la detección de inactividad no funciona**, y no
por culpa de la lógica (esa está probada), sino por cómo hay que hablar el
protocolo a mano.

**Reproducirlo** (no afecta a la app, es un proceso aparte que se rompe solo):

```console
$ python3 pausa.py --selftest
Segmentation fault (core dumped)
$ echo $?
139            # 139 = 128 + SIGSEGV(11)
```

Al arrancar la mascota se ve el aviso correspondiente:

```console
$ ./run.sh
[pausa] auto-test falló (rc=-11):
[pausa] ext-idle-notify-v1 no disponible: el auto-test de ext-idle-notify-v1 falló
[pausa] no hay forma de consultar la inactividad (ni ext-idle-notify-v1 ni
        MIT-SCREEN-SAVER); la pausa activa queda desactivada
```

**Por qué hace falta ctypes.** No hay binding de Python de Wayland instalado
(sin `pywayland`, sin `pywlroots`, sin `gi` para `ext-idle-notify-v1`), así que
la conexión se abre directamente contra `libwayland-client` 1.26. Choca de
entrada: `wl_display_get_registry()` y `wl_display_get_default_seat()` son
funciones *inline* del header, **no están exportadas**; solo se exportan
`wl_display_interface`, `wl_registry_interface` y `wl_seat_interface`.

**Qué sí se consiguió** (con `wl_proxy_marshal_array_flags`, en vez de la
variádica `wl_proxy_marshal_flags`, que con ctypes es frágil):

1. `wl_display.get_registry` → proxy del registro.
2. Listener del registro → localizar los globals. niri anuncia
   `ext_idle_notifier_v1` con **versión 2** y `wl_seat` con versión 9.
3. `wl_registry.bind` de `wl_seat` y de `ext_idle_notifier_v1`.
4. `wl_display_get_error()` == 0 en todos esos pasos: el compositor acepta
   los enlaces.

**Dónde se rompe:** al enviar la petición de notificación. Con la firma de la
**v1** (`get_ext_idle_notification(new_id, object seat, uint timeout)`, "oun",
opcode 1) el compositor responde con un error de protocolo, no con un fallo:

```console
wl_display#1: error 1: invalid arguments for ext_idle_notifier_v1#4.get_idle_notification
```

**La diferencia v1/v2 que se investigó.** El XML del protocolo declara
`ext_idle_notifier_v1 version="2"`, y la v2 **cambió el nombre y el orden de los
argumentos** de la petición:

| Versión | Petición (opcode 1) | Firma | Argumentos |
|---|---|---|---|
| v1 | `get_ext_idle_notification` | `oun` | `id`, `seat`, `timeout` |
| v2 | `get_idle_notification` | `nou` | `id`, `timeout`, `seat` |

(La v2 añade además `get_input_idle_notification` en el opcode 2.) El problema
de fondo es que **en el cable las dos versiones son idénticas** —tres palabras
de 4 bytes—, así que un orden equivocado no da error de marshalling: el
compositor lo decodifica al revés y responde `invalid arguments`. Probando
ambos órdenes, los dos dan ese error; y al hacerlo con las structs de interfaz
sintéticas a versión 2, la llamada peta dentro de
`wl_proxy_marshal_array_flags` (segfault).

Un detalle que costó encontrar: para un argumento `new_id` libwayland
**desreferencia** el puntero que se le pasa (`closure->args[i].n = object->id`),
así que pasar un `1` a mano como relleno provoca el fallo. Con la API variádica
hay además el problema de que ctypes mete enteros y punteros en registros
distintos de como los lee el `va_arg` de C. Con la API de array (`union
wl_argument`) el marshalling sí es correcto, pero el servidor sigue
rechazando la petición.

**Consecuencia y cómo arreglarlo.** Tal como está, en Wayland la pausa activa no
tiene forma de preguntar la inactividad, así que **queda desactivada** (y se
dice por consola, en vez de fingir que funciona). El código de la vía X11
(`XScreenSaverQueryInfo`) está escrito y debería funcionar en Xorg real, pero aquí
tampoco se pudo probar porque XWayland no expone `MIT-SCREEN-SAVER`.

Vías para arreglarlo, de menos a más trabajo:

1. **Instalar un binding real** de Wayland para Python (`python-wayland`, o
   `pywlroots`) y rehacer `WaylandIdle` con él: la API se reduce a enlazar el
   global y escuchar dos eventos. Con eso la pausa activa se activaría sola al
   arrancar, porque el auto-test ya es la única puerta de entrada.
2. **Usar una ruta específica del compositor** si existe (p. ej. un
   `IdleMonitor` por DBus): niri no implementa `org.gnome.Mutter.IdleMonitor`,
   pero otros setups podrían.
3. **Preguntar al usuario**: esta app es una mascota de escritorio, tiene un
   click-through y un menú; un "¿sigues ahí?" cada 50 min puede ser tan válido
   como mirar el reloj del servidor, y no depende de ningún protocolo exótico.

### API HTTP local

Apagada por defecto; se activa desde el menú (`API local: activar`). Escucha
**solo en 127.0.0.1:7777** y usa únicamente `http.server` de la biblioteca
estándar (sin dependencias). Sin autenticación: es un servicio local; cualquiera
con acceso a la máquina puede usarlo.

```bash
curl -s 127.0.0.1:7777/estado | python3 -m json.tool
curl -s 127.0.0.1:7777/rutinas
curl -s -X POST -d '{"texto":"hola","ms":3000}' 127.0.0.1:7777/decir
curl -s -X POST -d '{"texto":"aviso corto"}' 127.0.0.1:7777/aviso
curl -s -X POST -d '{"nombre":"siesta"}'       127.0.0.1:7777/rutina
curl -s -X POST -d '{"accion":"iniciar","formato":"45/10"}' 127.0.0.1:7777/pomodoro
```

| Ruta | Cuerpo | Efecto |
|---|---|---|
| `GET /estado` | — | Instantánea: sprite, rutina, globo, pomodoro, pausa, API, personaje, días de uso |
| `GET /rutinas` | — | Catálogo de rutinas y acciones |
| `POST /aviso` | `{"texto": "..."}` | Aviso corto (1,8 s) |
| `POST /decir` | `{"texto": "...", "ms": 4000}` | Globo con duración concreta |
| `POST /rutina` | `{"nombre": "pasear"}` | Lanza esa rutina |
| `POST /pomodoro` | `{"accion": "iniciar\|pausar\|reanudar\|saltar\|parar", "formato": "45/10"}` | Control del pomodoro |

Los `POST` se encolan y se ejecutan en el hilo principal de GTK (respuesta
`202`); los datos inválidos devuelven `400` con el detalle.

### Preferencias

`~/.config/mascota/prefs.json` (se crea solo):

```json
{
  "personaje": "naranja",
  "dias_uso": 3,
  "ultimo_dia": "2026-09-28",
  "formato_pomodoro": "25/5",
  "pausa_activa": true,
  "api_puerto": 7777
}
```

`dias_uso` cuenta los días naturales en los que se ha abierto la app (una vez
por día). `personaje` es el color del cuerpo (naranja, verde, violeta, rosa) y
se cambia desde el menú.

## Rendimiento

- Animación a 20 FPS; **5 FPS mientras duerme** (la siesta baja la frecuencia y
  el temporizador se reprograma).
- CPU medida: **0–1 %** en reposo con rutinas y API activas.
- El hilo HTTP nunca toca GTK: los `POST` se encolan y el `GET /estado` lee una
  instantánea que refresca el bucle principal.

## Compatibilidad (qué se verificó y qué no)

Entorno de prueba: **CachyOS + niri (Wayland) + XWayland**.

| Camino | Estado | Cómo se comprobó |
|---|---|---|
| Wayland + layer-shell (recomendado) | ✅ verificado | Capa `mascota` en Overlay/keyboard None; `wl_region.add(x, 32, 64, 64)` actualizándose; captura con el sprite visible y el contenido de atrás viéndose a través |
| Wayland sin layer-shell (fallback) | ✅ verificado | Aviso por consola; la ventana normal igual recibe `wl_region.add(...)` + `set_input_region` |
| X11 / XWayland | ✅ verificado | Shape de entrada = rect del sprite (y del globo cuando está visible); clic real inyectado con XTest → el salto se ejecutó; EWMH correcto |
| Rutinas y poses | ✅ verificado | Las 5 rutinas completan su ciclo; capturas de la siesta (con “Zzz”), la banca con el libro y el código con el portátil |
| Globo de texto | ✅ verificado | Captura con el globo, el rabito y el texto; su rect entra en la región de entrada |
| Pomodoro | ⚠️ parcial | Inicio, cambio de formato, salto de fase y el cambio de rutina por fase; **no** se esperó un bloque completo de 25/45/50 min |
| Menú de bandeja | ⚠️ parcial | `GetLayout` devuelve el árbol con submenús y `Event` funciona; **no** se hizo clic en el menú real del shell (todo por DBus) |
| Pausa activa (lógica) | ✅ verificado | Máquina de estados probada con un detector simulado (50 min → 3, 2, 1 → estirar → fin; cancelación por ausencia) |
| Pausa activa (detector real) | ❌ **no verificado** | Ver abajo |
| API HTTP | ✅ verificado | Los 6 endpoints probados con `curl`, incluidos 400 y 404 |
| Preferencias | ✅ verificado | Fichero creado y leído; `personaje` y `dias_uso` |
| CPU / 5 FPS al dormir | ✅ verificado | 0–1 %; `fps=5` mientras `durmiendo=true` |
| Xorg real (no XWayland) | ❌ no probado | Solo hay sesión Wayland en esta máquina |
| GNOME/KDE Wayland (sin `zwlr_layer_shell`) | ❌ no probado | Sin layer-shell el backend avisa y sigue con ventana normal |
| i3 / bspwm / Openbox | ❌ no probado | Ver limitación de `struts` más abajo |
| Clic real sobre la mascota en Wayland | ⚠️ parcial | Verificado a nivel de protocolo Wayland; no hubo herramienta para inyectar puntero (`wtype`/`ydotool` no instaladas) |
| Posición “abajo de todo” en X11 | ⚠️ parcial | Funciona con un WM X11 clásico; **en XWayland+niri `XMoveWindow` es ignorado** |

## Lo que NO pude verificar

1. **Detección de inactividad en Wayland (`ext-idle-notify-v1`).** No hay
   binding de Python instalado, así que se habló el protocolo a mano con
   `ctypes` sobre `libwayland-client` 1.26. Se consiguió enlazar el global y
   `wl_seat` (`bind` con `wl_registry_interface` y `wl_display_interface`
   exportadas), pero la llamada `get_idle_notification` provoca un **fallo de
   segmentación** dentro de `wl_proxy_marshal_array_flags`, y niri además
   responde `invalid arguments` con la firma de la v1. La v2 del protocolo
   reordered los argumentos (`nou`) y reordenar no bastó. Por eso la
   implementación va siempre precedida de un auto-test en subproceso: si peta,
   la pausa activa se desactiva con un aviso en vez de tumbar la app.
   *Cómo lo probé:* `python3 pausa.py --selftest`.
2. **`MIT-SCREEN-SAVER` en X11.** El camino está implementado
   (`XScreenSaverQueryInfo`), pero **XWayland no expone esa extensión** en esta
   máquina, así que no se pudo leer un tiempo de inactividad real. En Xorg con
   un WM real debería funcionar, pero está sin probar.
3. **La pausa activa de principio a fin.** Sin detector, los 50 minutos no se
   pueden esperar en una prueba; se probó la lógica con un detector simulado.
4. **Un ciclo completo de pomodoro** (25/45/50 min reales) y la transición
   automática trabajo → descanso → trabajo.
5. **El menú de bandeja en el shell real**: se verificó por DBus
   (`GetLayout`/`Event`), no abriendo el menú con el ratón.
6. **Other escritorios**: nada más que niri se ha probado.

## Limitaciones conocidas

1. **niri: una ventana *toplevel* enfocada se rellena de lavanda.**
   Cuando niri enfoca una ventana normal (X11 **o** Wayland sin layer-shell)
   dibuja su efecto de fondo (focus-ring con degradado `#9ccbfb → #d4bee6`, de
   la paleta del wallpaper) *detrás* de la ventana. Como la ventana es
   transparente, ese relleno se ve entero. Se comprobó que **sin foco la
   ventana es transparente de verdad** y que la **layer-surface con `keyboard
   NONE` nunca toma foco** → transparencia correcta.

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
   así que la regla solo afecta a la mascota. Ojo al punto y coma:
   `focus-ring { off; }`, no `focus-ring { off }` (KDL lo rechaza).

   *Contrapartida:* en niri la ventana con `--x11` es una *tile* más del layout
   y, al no tomar el foco, niri no desplaza la vista: puede quedar fuera de
   pantalla. La ruta Wayland con layer-shell no le afecta.
2. **XWayland ignora `XMoveWindow`.** La ventana X11 queda donde la coloque el
   compositor (niri la hace *tile*), no abajo del todo. En Xorg con un WM
   clásico sí funcionaría.
3. **`_NET_WM_WINDOW_TYPE_DOCK` puede reservar struts** en i3/bspwm y dejar
   una franja muerta al final de la pantalla. Está pendiente de probar; si
   pasa, cambiar a `_NET_WM_WINDOW_TYPE_NOTIFICATION` en `backends/x11.py`.
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
   la muestra flotando en mitad de pantalla. Sirve para comprobar el
   click-through, pero para tener la mascota abajo del todo hace falta
   layer-shell (Wayland) o `--x11` (X11 clásico).
9. **El globo usa la tipografía “toy” de Cairo** (sin Pango): no hay
   acentos, subrayado ni ajuste de línea, y la fuente depende de la que
   tenga Cairo. Es suficiente para frases cortas.

## Estructura

```
mascota/
├── main.py           # coordinación: backend, animación, dibujo, menú, API
├── rutinas.py        # motor de rutinas + las 5 rutinas
├── objetos.py        # banca, libro, taza, portátil
├── globo.py          # globo de texto con Cairo
├── pomodoro.py       # 25/5, 45/10, 50/10
├── pausa.py          # inactividad (ext-idle-notify / XScreenSaver) + estiramiento
├── api.py            # API HTTP en 127.0.0.1:7777 (http.server)
├── preferencias.py   # ~/.config/mascota/prefs.json
├── sprite.py         # frames pixel-art 16x16, poses y caras
├── tray.py           # bandeja StatusNotifierItem por DBus
├── run.sh            # lanzador con comprobaciones
└── backends/
    ├── __init__.py
    ├── base.py       # set_input_region() vía GDK (X11 y Wayland)
    ├── wayland.py    # gtk4-layer-shell + fallback
    └── x11.py        # EWMH + XMoveWindow con ctypes
```
