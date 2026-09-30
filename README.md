<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=1,4,8,12&height=180&section=header&text=MASKOT&fontSize=50&fontColor=ffffff&fontAlignY=38&desc=Mascota%20de%20Escritorio%20en%20Pixel%20Art%20para%20Linux&descAlignY=60&descAlign=50" width="100%" alt="Maskot Header" />

<img src="https://readme-typing-svg.demolab.com?font=Press+Start+2P&size=13&duration=3000&pause=1000&color=FBBF24&center=true&vCenter=true&width=650&lines=Mascota+pixel+art+16x16+nativa+para+Linux;Ventana+transparente+con+click-through+real;Pomodoro%2C+rutinas+aut%C3%B3nomas+y+API+local;Ultra+ligero%3A+0-1%25+CPU+(5+FPS+al+dormir)" alt="Typing SVG" />

<br/>

[![Release](https://img.shields.io/badge/Versi%C3%B3n-Beta%20Fase%202-E60012?style=for-the-badge&logo=retroarch&logoColor=white)](https://github.com/andrwvaz2/maskot-linux)
[![Platform](https://img.shields.io/badge/Plataforma-Wayland%20%7C%20X11-FFCC00?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/andrwvaz2/maskot-linux)
[![Engine](https://img.shields.io/badge/Motor-Python%203%20%2B%20GTK4-306998?style=for-the-badge&logo=python&logoColor=white)](https://www.gtk.org/)
[![Graphics](https://img.shields.io/badge/Gr%C3%A1ficos-Cairo%20Pixel%20Art-FF5722?style=for-the-badge)](https://cairographics.org/)
[![Performance](https://img.shields.io/badge/CPU-0--1%25%20Idle-4E9F3D?style=for-the-badge)](https://github.com/andrwvaz2/maskot-linux)
[![License](https://img.shields.io/badge/Licencia-Open%20Source-008080?style=for-the-badge)](https://github.com/andrwvaz2/maskot-linux)

<br/>

```text
┌────────────────────────────────────────────────────────────────────────┐
│  ▶ MASKOT v0.2.0-beta [SYSTEM READY]                                   │
│                                                                        │
│  "Un compañero virtual en pixel art para tu escritorio Linux.          │
│   Flota con transparencia total, permite clicks a través de su cuerpo, │
│   toma siestas a 5 FPS y te acompaña con Pomodoro mientras programas." │
└────────────────────────────────────────────────────────────────────────┘
```

</div>

---


### 🎭 Elenco de Personajes (9 Mascotas Disponibles)
Puedes cambiar de compañero en cualquier momento desde el submenú de la bandeja o mediante la API HTTP:

| Mascota | Especie | Paleta Distintiva | Personalidad / Rol |
|:---:|:---:|:---|:---|
| 🐧 **Tux** *(Default)* | Pingüino | Carbón, Blanco y Amarillo `#F59E0B` | El legendario guardián de Linux |
| 🦀 **Koru** | Cangrejo | Terracota `#F26A2E` y puntas azul claro | El explorador curioso del sistema |
| 🧢 **Clawd** | Cangrejo | Terracota `#D97757` con gorra azul marino | El clásico deportivo con gorra hacia atrás |
| 🦊 **Tuno** | Zorro | Naranja `#F58A2A`, crema y cian | El estratega creativo; encuentra atajos |
| 🐢 **Nilo** | Tortuga | Verde `#A8DB55` y caparazón teal `#249CB8` | Confiable y constante; nunca falla |
| 🐝 **Brio** | Abeja | Amarillo `#F5D338` y alas celestes | La ejecutora veloz y enfocada |
| 🦉 **Luma** | Búho | Morado `#9B6AE3` y plumas azul cielo | La analista observadora de detalles |
| 🦎 **Mako** | Gecko | Turquesa `#44D0CF` y verde lima | El ágil y adaptable; aprende rápido |
| 🐙 **Orbi** | Pulpo | Coral `#F56B8A` y tentáculos lavanda | El integrador multitarea que conecta todo |

---

## ⚡ Características Principales

- 🪟 **Ventana Transparente con Click-Through Real:** La ventana flota en pantalla sin marcos ni fondo. El puntero del ratón atraviesa todo el espacio vacío (`Gdk.Surface.set_input_region`), interactuando únicamente cuando haces clic sobre el sprite o sobre su globo de diálogo.
- 🤖 **Rutinas Autónomas Dinámicas:** Motor con pesos probabilísticos que decide qué hacer cada 20–40 segundos (pasear, escribir código en su laptop, leer en una banca, dormir siestas, tomar un café, echar una hoja a la papelera, regar la plantita o respirar).
- 🍅 **Temporizador Pomodoro:** Modos `25/5`, `45/10` y `50/10`. La mascota sincroniza sus acciones según la fase: programa o lee en tiempo de trabajo, y toma café en los descansos.
- 🧘 **Pausa Activa (Salud Postural):** Tras 50 minutos de uso continuo, Maskot inicia una cuenta regresiva (3, 2, 1) y ejecuta una pose de estiramiento guiado de 6 segundos.
- 💬 **Globo de Texto Vectorial (Cairo):** Renderizado con sombra y rabito direccional. El área del globo se suma a la región de entrada para permitir interacción con el mensaje.
- 🛎️ **Bandeja del Sistema (StatusNotifierItem):** Menú rápido por DBus nativo con submenús para alternar colores, rutinas, temporizadores y opciones.
- 🌐 **API HTTP Local (`127.0.0.1:7777`):** Controla a Maskot desde scripts, terminal o atajos de teclado con llamadas sencillas vía `curl`.
- 🔋 **Ahorro de Recursos Legendario:** 20 FPS en actividad y **5 FPS durante la siesta**, manteniendo el uso de CPU entre 0% y 1%.

---

## 🕹️ Catálogo de Rutinas & Comportamiento

Maskot ejecuta secuencias de micro-acciones de forma autónoma:

```text
  ╔═════════════════════════════════════════════════════════════════════════════╗
  ║                           RUTINAS DISPONIBLES                               ║
  ╠═════════════════════════════════════════════════════════════════════════════╣
  ║  • PASEAR       : Explora la barra inferior caminando a un punto al azar.   ║
  ║  • SIESTA       : Cierra los ojos, baja a 5 FPS y emite "Zzz" en reposo.    ║
  ║  • LEER BANCA   : Coloca una banca de madera y saca su libro pixel art.     ║
  ║  • ECHAR CÓDIGO : Abre su mini laptop y se pone a programar contigo.        ║
  ║  • CAFÉ BREAK   : Disfruta de una taza humeante en los descansos Pomodoro.  ║
  ║  • HOJA A PAPELERA: Recoge una hoja del suelo y la tira a una papelera.     ║
  ║  • PLANTITA     : Riega su maceta; crece según los días de uso que llevas.  ║
  ║  • RESPIRAR     : Cuenta atrás 3-2-1 y dos rondas de inhalar/exhalar.       ║
  ║  • SALTO REACTIVO: ¡Hazle clic en cualquier momento para saludar!           ║
  ╚═════════════════════════════════════════════════════════════════════════════╝
```

> [!TIP]
> ¿Quieres ver una rutina concreta sin esperar a que salga al azar? Lánzala forzada
> al arrancar: `MASKOT_DEMO=matica:loop python3 main.py` (o `python3 main.py --demo
> matica:loop`). Sin `:loop` la ejecuta una sola vez. El nombre de la rutina
> también se puede forzar en caliente desde la API: `curl -d '{"nombre":
> "respiracion"}' 127.0.0.1:7777/rutina`.

### Primitivas del Motor (`rutinas.py`)

| Acción | Efecto |
|---|---|
| `ir_a(x, al_llegar=…)` | Desplaza el sprite a la posición horizontal `x` (`None` para destino aleatorio). Con `al_llegar=True` la rutina continúa en cuanto llega. |
| `decir(texto, ms)` | Muestra un texto en el globo de diálogo durante `ms` milisegundos. |
| `cara(nombre, ms)` | Cambia la expresión del rostro: `feliz`, `cansado`, `pensar`. |
| `esperar(ms, pose=…, texto=…)` | Pausa en el lugar con una pose (`siesta`, `leer`, `codigo`, `regar`, `respirar`) y, si se le pasa `texto`, lo muestra mientras espera. |
| `objeto(nombre, x=…, y=…)` | Coloca o mueve un elemento del escenario (`banca`, `libro`, `taza`, `portatil`, `papelera`, `hoja`, `regadera`, `planta_*`). |
| `quitar(nombre)` | Retira un solo objeto y deja los demás donde estaban. |
| `cuenta_atras(n, ms, texto)` | Cuenta `3…2…1` en el globo. Es la misma cuenta que usa la pausa activa (`pausa.CuentaAtras`). |
| `saltar()` | Efectúa un salto elástico con animación. |
| `fin()` | Finaliza la rutina y cede el turno al selector aleatorio. |

> [!TIP]
> Cualquier clic del usuario sobre el sprite cancela de inmediato la rutina en curso y hace que Maskot dé un salto amistoso.

---

## 🎒 Módulos Integrados

### 🍅 Temporizador Pomodoro
Se activa y gestiona desde la bandeja del sistema o la API HTTP.
- **Formatos:** `25/5` (estándar), `45/10` (largo) y `50/10` (intensivo).
- **Indicador:** Tiempo restante visible en el menú contextual y en el tooltip del icono.
- **Sincronización:** Durante el **bloque de trabajo**, Maskot lee o programa en su laptop; durante el **descanso**, toma una taza de café caliente.

### 🧘 Pausa Activa
- Monitorea el tiempo de uso continuo de la pantalla.
- Al acumular **50 minutos ininterrumpidos**, propone un estiramiento con cuenta atrás (3, 2, 1) y mantiene la pose durante 6 segundos.
- Si detecta que te ausentas (≥ 1 minuto de inactividad), la cuenta se reinicia sola.

### 💾 Preferencias Persistentes
Las preferencias se almacenan automáticamente en `~/.config/mascota/prefs.json`:
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
- `dias_uso`: Contador de días naturales en los que has utilizado la app. También marca en qué etapa está la plantita de la rutina `matica`: hasta 2 días es una semilla, a partir del tercero un brote y del día 15 en adelante florecida. Al regarla da un estirón y crece una etapa (hasta florecida).

---

## 💻 Requisitos del Sistema

- **Python 3** (verificado en 3.14)
- **PyGObject** con **GTK 4** (verificado en 4.22)
- **pycairo**
- **gtk4-layer-shell** (requerido para Wayland mediante el protocolo `zwlr_layer_shell_v1`)

---

## ⚡ Instalación Rápida & Configurador Multi-WM

Maskot incluye un instalador interactivo [install.sh](file:///home/andrw/mascota/install.sh) que detecta automáticamente tu gestor de paquetes, comprueba dependencias y permite inyectar reglas de ventana para tu compositor o entorno.

> [!WARNING]
> **Estado de compatibilidad por entorno:**
> - **niri (+ XWayland):** 🟢 **Probado** activamente en el entorno de desarrollo.
> - **Hyprland, Sway, i3, bspwm, GNOME, KDE, XFCE:** ⚠️ **No probadas**.
> El instalador **nunca aplicará reglas en silencio ni modificará tu configuración sin tu permiso expreso**: te mostrará la regla propuesta y te preguntará `¿aplicar esta regla a tu config? [s/N]` (por defecto **No**). Para paquetes del sistema, también te solicitará confirmación (`[s/N]`).

### Opción A — Modo simulación sin tocar el sistema (`--dry-run`):
```bash
# Inspecciona qué comandos, rutas y reglas se aplicarían sin modificar nada:
curl -sSL https://raw.githubusercontent.com/andrwvaz2/maskot-linux/main/install.sh | bash -s -- --dry-run
# O si ya clonaste el repositorio:
./install.sh --dry-run
```

### Opción B — Un solo comando (One-Liner vía curl):
```bash
curl -sSL https://raw.githubusercontent.com/andrwvaz2/maskot-linux/main/install.sh | bash
```

### Opción C — Clonando el repositorio:
```bash
git clone https://github.com/andrwvaz2/maskot-linux.git
cd maskot-linux
./install.sh
```

También puedes ejecutarlo de manera directa para tu entorno específico o de forma desatendida:

```bash
# 1. Modo simulación (dry-run):
./install.sh --dry-run         # Muestra qué se escribiría sin modificar archivos

# 2. Entorno probado y verificado:
./install.sh --wm niri         # [Probado] Aplica regla anti focus-ring lavanda en niri

# 3. Entornos NO PROBADOS (muestran la regla y piden confirmación [s/N] antes de escribir):
./install.sh --wm hyprland     # [No probada] Pregunta antes de escribir en hyprland.conf
./install.sh --wm sway         # [No probada] Pregunta antes de escribir en sway/config
./install.sh --wm i3           # [No probada] Pregunta antes de escribir en i3/config
./install.sh --wm bspwm        # [No probada] Pregunta antes de escribir en bspwmrc
./install.sh --wm gnome        # [No probada] Lanzador compatible con XWayland (--x11)
./install.sh --wm kde          # [No probada] Integración con KWin y bandeja del sistema
./install.sh --wm xfce         # [No probada] Soporte dock EWMH tradicional
./install.sh --wm generic      # Configuración genérica sin reglas de compositor

# 4. Banderas de automatización:
./install.sh --autostart       # Activa inicio automático con la sesión
./install.sh --no-deps         # Omite instalación de paquetes del sistema
./install.sh --uninstall       # Elimina binarios, accesos directos e iconos
```

### ¿Qué hace el instalador?
1. 🛡️ **Modo Dry-Run (`-n, --dry-run`):** Permite simular la instalación completa para auditar paquetes, rutas y reglas de ventana sin modificar nada en tu disco.
2. 📦 **Dependencias:** Comprueba paquetes según tu distro (`pacman`, `apt`, `dnf`, `zypper`). Si faltan dependencias, te muestra el comando y solicita confirmación interactiva (`[s/N]`, nunca en silencio).
3. 🪟 **Reglas de WM:**
   - En **niri** *(probado)*: Aplica la regla `focus-ring { off; }` y `open-focused false`.
   - En **Hyprland, Sway, i3, bspwm** *(no probadas)*: Muestra la regla propuesta y te pide confirmación `¿aplicar esta regla a tu config? [s/N]` antes de tocar el archivo, generando un respaldo `.bak` previo si confirmas.
4. 🚀 **Comando Global:** Instala `maskot` en `~/.local/bin/maskot` para lanzarlo desde cualquier terminal.
5. 🎨 **Lanzador de Escritorio:** Instala el archivo `maskot.desktop` y el icono pixel art oficial en formato SVG.
6. 🔄 **Autostart:** Te pregunta `[s/N]` si deseas iniciar Maskot al encender tu PC.

---

## 🚀 Ejecución Manual

Si prefieres ejecutar Maskot sin instalarlo en el sistema, puedes usar directamente el lanzador [run.sh](file:///home/andrw/mascota/run.sh):

```bash
# 1. Ejecución estándar (autodetecta Wayland o X11)
./run.sh

# 2. Forzar backend X11 / XWayland
./run.sh --x11

# 3. Escalar sprite a 8x (128 px, por defecto 4x = 64 px)
./run.sh --scale 8
```

O lanzamiento manual con Python:
```bash
python3 main.py [--x11] [--scale N] [--demo RUTINA[:loop]]
                [--monitor CONECTOR|ÍNDICE] [--list-monitores]
```

Opciones y su equivalente como variable de entorno:

| Flag | Variable | Qué hace |
|---|---|---|
| `--demo matica:loop` | `MASKOT_DEMO=matica:loop` | Arranca esa rutina al abrir la ventana; `:loop` la repite. |
| `--monitor HDMI-A-1` / `--monitor 1` | `MASKOT_MONITOR=HDMI-A-1` | Fija en qué monitor se dibuja la barra (por defecto, el primero que vea GDK). |
| `--list-monitores` | — | Lista los conectores disponibles y sale. |

---

## 📡 API HTTP Local (`127.0.0.1:7777`)

Maskot incluye un servidor HTTP local ultraligero (`http.server` de la biblioteca estándar, sin dependencias externas). Viene apagado por defecto y se activa desde el menú de la bandeja (`API local: activar`).

Las peticiones `POST` se procesan de forma segura en el bucle principal de GTK mediante `GLib.idle_add`:

```bash
# Consultar estado global del sistema
curl -s 127.0.0.1:7777/estado | python3 -m json.tool

# Ver catálogo de rutinas
curl -s 127.0.0.1:7777/rutinas

# Mostrar un mensaje en el globo de texto (ms personalizados)
curl -s -X POST -d '{"texto": "¡Hola desde la terminal!", "ms": 3500}' 127.0.0.1:7777/decir

# Notificación rápida (1.8 segundos)
curl -s -X POST -d '{"texto": "Tarea completada ✨"}' 127.0.0.1:7777/aviso

# Activar una rutina específica
curl -s -X POST -d '{"nombre": "siesta"}' 127.0.0.1:7777/rutina

# Controlar el Pomodoro
curl -s -X POST -d '{"accion": "iniciar", "formato": "25/5"}' 127.0.0.1:7777/pomodoro
curl -s -X POST -d '{"accion": "pausar"}' 127.0.0.1:7777/pomodoro

# Cambiar de personaje (tux, koru, clawd, tuno, nilo, brio, luma, mako, orbi)
curl -s -X POST -d '{"nombre": "tux"}' 127.0.0.1:7777/personaje
```

### Tabla de Endpoints

| Método | Endpoint | Cuerpo JSON | Descripción |
|:---:|---|---|---|
| `GET` | `/estado` | — | Snapshot del estado: sprite, rutina, globo, pomodoro, pausa, personaje y días de uso |
| `GET` | `/rutinas` | — | Catálogo de rutinas y micro-acciones |
| `POST` | `/aviso` | `{"texto": "..."}` | Globo rápido de advertencia (1.8 s) |
| `POST` | `/decir` | `{"texto": "...", "ms": 3000}` | Mensaje con duración específica en ms |
| `POST` | `/rutina` | `{"nombre": "siesta"}` | Interrumpe y ejecuta la rutina indicada |
| `POST` | `/pomodoro` | `{"accion": "...", "formato": "..."}` | Iniciar, pausar, reanudar, saltar o parar el Pomodoro |
| `POST` | `/personaje` | `{"nombre": "tux"}` | Cambia la mascota activa en tiempo real |

---

## 🗺️ Matriz de Compatibilidad

Verificado internamente en: **CachyOS + niri (Wayland) + XWayland**.

Leyenda de la columna *Estado*:

- 🟢 **Verificado**: reproducido y comprobado por el equipo.
- 📌 **Reporte de comunidad**: confirmado por un usuario externo; **no** se ha reproducido ni verificado internamente.
- 🟡 / ⚠️ / 🔴: funcional parcial, sin probar o pendiente.

### Compositores y Window Managers
| Compositor / Entorno | Estado | Detalle de Verificación |
|---|:---:|---|
| **niri** (Wayland) | 🟢 Verificado | Regla en `cfg/rules.kdl` probada; capa `OVERLAY`, click-through y anti *focus-ring* lavanda. |
| **Hyprland** (Wayland) | ⚠️ No probada | Reglas `layerrule` / `windowrulev2` propuestas; requiere confirmación interactiva `[s/N]`. |
| **Sway / River** (Wayland) | ⚠️ No probada | Reglas `floating` / `sticky` propuestas; requiere confirmación interactiva `[s/N]`. |
| **i3wm / bspwm** (X11) | ⚠️ No probada | Reglas de flotación propuestas; requiere confirmación interactiva `[s/N]`. |
| **GNOME** (Wayland / X11) | ⚠️ No probada | Modo adaptativo XWayland (`--x11`) propuesto en lanzador. |
| **KDE Plasma** (Wayland / X11) | ⚠️ No probada | Integración KWin propuesta sin inyección invasiva. |
| **XFCE** (X11) | 📌 Reporte de comunidad | Alguien reporta que **corre correctamente**. **Sin detalles técnicos ni verificación interna, y sin referencia enlazada**: no consta versión de XFCE, versión de Maskot ni si usó sesión X11 nativa o `--x11`. No tomar como cobertura probada. |
| **MATE** (X11) | ⚠️ No probada | Integración dock EWMH tradicional propuesta. |

### Componentes y Funcionalidades
| Componente | Estado | Detalle de Verificación |
|---|:---:|---|
| **Wayland + layer-shell** *(Recomendado)* | 🟢 Verificado | Capa `mascota` en `OVERLAY`, teclado `NONE`, superficie a todo el ancho del monitor (por defecto el primer monitor de GDK; configurable con `--monitor`/`MASKOT_MONITOR`). Click-through fluido con `wl_region`. |
| **Wayland sin layer-shell** *(Fallback)* | 🟡 Funcional | Modo ventana flotante; avisa en consola y mantiene `set_input_region`. |
| **X11 / XWayland** | 🟢 Verificado | Shape recortado al sprite y globo. Inyección de clic XTest verificada. |
| **Rutinas y Objetos** | 🟢 Verificado | Las 8 rutinas completan su ciclo (banca, libro, laptop, taza, siesta, papelera, plantita, respiración). Secuencias comprobadas sin ventana; las 3 nuevas a falta de revisión visual en pantalla. |
| **Globo de Diálogo** | 🟢 Verificado | Renderizado Cairo nítido con sombra y rabito direccional. |
| **Temporizador Pomodoro** | 🟡 Parcial | Estados, cambios de fase y avisos probados; falta prueba continua de 50 min. |
| **Bandeja de Estado (DBus)** | 🟡 Parcial | Árbol de submenús `GetLayout` y eventos validados vía DBus. |
| **Pausa Activa (Lógica)** | 🟢 Verificado | Máquina de estados validada con detector simulado (50 min → 3,2,1 → estirar). |
| **Pausa Activa (Sensor Real)** | 🔴 Pendiente | Detalles técnicos explicados en las notas de desarrollo. |
| **Consumo a 5 FPS (Siesta)** | 🟢 Verificado | 0–1% CPU medido en reposo con reprogramación dinámica de FPS. |

---

## 🔬 Notas de Desarrollo & Hacks del Sistema

<details>
<summary><b>📐 Monitor y ancho de la barra en Wayland (layer-shell) (Clic para desplegar)</b></summary>
<br>

**Síntoma (ya corregido):** la ventana medía 200 px de ancho (lo reportaba el propio dibujo como `window_width=200`) en vez de cubrir el monitor, así que la mascota solo se movía por los primeros 136 px y los objetos de las rutinas se quedaban fuera de la ventana.

**Causa:** `gtk4-layer-shell` no expone `set_size`: pide el tamaño a la ventana con `gtk_window_get_default_size` y lo manda como tamaño de la layer-surface. Al llamar a `set_default_size(0, alto)` GTK resuelve el ancho 0 a su mínimo, que son 200 px, y esa es la superficie que acaba usando el compositor aunque esté anclada a izquierda y derecha.

**Corrección:** `WaylandBackend._dimensionar()` pide el ancho real de la salida (`Gdk.Monitor.get_geometry()`) para que la barra cubra el monitor entero, igual que hace el backend X11.

### En cuál monitor se dibuja

- **Por defecto usa el primero de la lista de GDK**, es decir `get_monitors()[0]`. **No** es "el monitor enfocado" ni un monitor "principal".
- Ojo: en GTK 4.22 no existe `Gdk.Monitor.is_primary()`, y **el orden de `get_monitors()` lo impone el compositor** (el orden en que anuncia sus salidas), así que **puede cambiar entre sesiones o al conectar/desconectar pantallas**. Por eso el valor por defecto no es estable en multi-monitor; para eso está la opción de abajo.
- La misma salida se usa para medir el ancho y para fijar la ventana (`set_monitor`), de modo que las dos cosas no se contradigan.

#### Cómo elegir monitor

Primero, listar los conectores:

```bash
python3 main.py --list-monitores
```

```text
[0] HDMI-A-1     1920x1080+0+0  DELL SE2425H (Dell Inc.)
[1] eDP-1       1920x1080+0+0  Panel Built-in (LG Display)
```

Y luego fijarlo, por conector o por índice (funciona en los dos backends):

```bash
MASKOT_MONITOR=HDMI-A-1 python3 main.py    # por conector
python3 main.py --monitor 1               # por índice (equivalente)
```

El conector se puede poner en minúsculas y abreviado como prefijo (`hdmi` → `HDMI-A-1`). Si el nombre no existe o el índice está fuera de rango, sale un aviso con la lista de conectores y se usa el primero de la lista.
</details>

<details>
<summary><b>⚠️ Estado de la Detección de Inactividad en Wayland (Clic para desplegar)</b></summary>
<br>

A diferencia de X11 (`MIT-SCREEN-SAVER`), en Wayland no existe una API de inactividad global directa sin permisos especiales.

**Situación actual:**
- Sin bindings empaquetados en Python (`pywayland` / `pywlroots`), la app interactúa con `libwayland-client 1.26` mediante `ctypes`.
- El protocolo `ext-idle-notify-v1` versión 2 reordenó los argumentos de `get_idle_notification` (`nou` frente a `oun`). Al realizar el marshalling a bajo nivel en C con `wl_proxy_marshal_array_flags`, `libwayland` desreferencia punteros de ID generando un fallo de segmentación (`SIGSEGV`, código 139).
- **Protección implementada:** Maskot ejecuta un auto-test en subproceso (`python3 pausa.py --selftest`): si el detector falla, desactiva la pausa activa de forma limpia con un aviso por consola, **evitando cualquier caída de la aplicación**.

**Vías de resolución previstas:**
1. Instalar bindings nativos como `python-wayland`.
2. Integrar monitores de inactividad por DBus según el compositor (`org.gnome.Mutter.IdleMonitor`, etc.).
3. Modo alternativo con confirmación interactiva en pantalla ("¿Sigues ahí?").
</details>

<details>
<summary><b>🪟 Regla de Ventana para el Compositor niri (Clic para desplegar)</b></summary>
<br>

En compositores como `niri`, enfocar una ventana transparente puede provocar que se pinte el anillo de foco (*focus-ring* lavanda) detrás de la ventana.

Para solucionarlo, añade esta regla a tu archivo `~/.config/niri/cfg/rules.kdl`:
```kdl
window-rule {
    match title="^Mascota$"
    open-focused false
    focus-ring { off; }
}
```
*(El título de la ventana es exactamente `Mascota`, por lo que la regla solo afecta a esta app).*
</details>

<details>
<summary><b>🧩 Detalles de Enlace, Bandeja y Fuentes (Clic para desplegar)</b></summary>
<br>

- **Orden de Enlace de `gtk4-layer-shell`:** Debe cargarse antes de `libwayland`. `run.sh` lo soluciona precargando la librería con `LD_PRELOAD`.
- **Bandeja sin librerías obsoletas:** Se evita `libayatana-appindicator` (ligada a GTK3). En su lugar, `tray.py` implementa el protocolo StatusNotifierItem nativamente vía DBus con `Gio`.
- **Tipografía "Toy" de Cairo:** Los globos utilizan la API tipográfica ligera de Cairo para no acarrear dependencias de Pango.
</details>

---

## 📁 Estructura del Proyecto

```text
mascota/
├── main.py              # Bucle principal, renderizado Cairo, coordinación y eventos
├── rutinas.py           # Motor de micro-acciones y catálogo de las 8 rutinas
├── objetos.py           # Sprites pixel art de objetos (banca, libro, portátil, taza, papelera, hoja, regadera, plantita)
├── globo.py             # Globo de texto Cairo con rabito direccional y sombra
├── pomodoro.py          # Lógica del temporizador Pomodoro (25/5, 45/10, 50/10)
├── pausa.py             # Máquina de estados de pausa activa y auto-test en Wayland
├── api.py               # Servidor HTTP local REST (127.0.0.1:7777) sin dependencias
├── preferencias.py      # Persistencia en disco (~/.config/mascota/prefs.json)
├── sprite.py            # Motor de renderizado Cairo, poses y animación
├── personajes.py        # Catálogo de 9 personajes (Tux + Familia Koru)
├── tray.py              # Icono y menú en la bandeja del sistema vía DBus puro
├── run.sh               # Lanzador con detección de entorno y comprobación de libs
├── install.sh           # Instalador interactivo y configurador multi-WM/escritorios
├── assets/
│   ├── maskot.svg       # Icono pixel art oficial en formato vectorial
│   └── maskot.desktop   # Lanzador estándar XDG para menús y autostart
└── backends/
    ├── __init__.py      # Selector dinámico de backend
    ├── base.py          # Regiones de click-through (set_input_region) con GDK
    ├── wayland.py       # Integración con gtk4-layer-shell y modo fallback
    └── x11.py           # Ventana EWMH (DOCK/ABOVE) y posicionamiento XLib
```

---

## 🏆 Créditos & Atribución

Este proyecto es una **implementación original e independiente para Linux** escrita en Python y GTK4, inspirada en [alecap92/maskot-mac](https://github.com/alecap92/maskot-mac).

- **Diseños de personajes:** Los sprites y paletas de la Familia Koru (*Koru, Clawd, Tuno, Nilo, Brio, Luma, Mako, Orbi*) fueron adaptados de [alecap92/maskot-mac](https://github.com/alecap92/maskot-mac) bajo la **Licencia MIT** (*Copyright (c) 2026 alecap92*).
- **Tux (Linux):** Diseño en pixel art 16×16 creado originalmente para esta versión nativa de Linux.
- **Arquitectura:** Toda la base de código para Linux (servidor Wayland layer-shell, X11 EWMH, click-through en Cairo, menú DBus y API HTTP) ha sido escrita desde cero.

---

<div align="center">

**¿Listo para probarlo? ¡Lanza `./run.sh` en tu terminal!**  
*Desarrollado con ☕, píxeles y cariño por el software libre.*

</div>
