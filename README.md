# 👾 MASKOT — Mascota de Escritorio en Pixel Art (Edición GBC)

<div align="center">

```text
  ██████╗  ██████╗ ██╗  ██╗███████╗███╗   ███╗ ██████╗ ███╗   ██╗
  ██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝████╗ ████║██╔═══██╗████╗  ██║
  ██████╔╝██║   ██║█████╔╝ █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║
  ██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║
  ██║     ╚██████╔╝██║  ██╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
  ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
  ★ G A M E   B O Y   C O L O R   S T Y L E   L I N U X   P E T ★
```

[![Release](https://img.shields.io/badge/Versi%C3%B3n-Beta%20Fase%202-E60012?style=for-the-badge&logo=nintendo&logoColor=white)](https://github.com/andrwvaz2/maskot-linux)
[![Platform](https://img.shields.io/badge/Plataforma-Wayland%20%7C%20X11-FFCC00?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/andrwvaz2/maskot-linux)
[![Engine](https://img.shields.io/badge/Motor-Python%203%20%2B%20GTK4-306998?style=for-the-badge&logo=python&logoColor=white)](https://www.gtk.org/)
[![Graphics](https://img.shields.io/badge/Gr%C3%A1ficos-Cairo%20Pixel%20Art-FF5722?style=for-the-badge)](https://cairographics.org/)
[![License](https://img.shields.io/badge/Licencia-Open%20Source-008080?style=for-the-badge)](https://github.com/andrwvaz2/maskot-linux)

```text
┌────────────────────────────────────────────────────────────────────────┐
│  ¡Un MASKOT salvaje ha aparecido en el borde de tu pantalla!           │
│                                                                        │
│  "Un compañero virtual en pixel art 16x16 nativo para Linux.           │
│   Flota con transparencia total, permite clicks a través de su         │
│   cuerpo, toma siestas a 5 FPS y te cuida con técnicas Pomodoro."      │
└────────────────────────────────────────────────────────────────────────┘
```

</div>

---

## 📟 Pokédex Regional de Linux

```text
  ▼ FICHA DE DATOS #001 — MASKOT (EDICIÓN LINUX) ▼
  ┌──────────────────────────────┬────────────────────────────────────────┐
  │         ▄▄▄▄▄▄▄▄▄▄           │ NOMBRE:    Maskot                      │
  │       ▄████████████▄         │ ESPECIE:   Mascota de Escritorio       │
  │      ████████████████        │ TIPO:      SISTEMA / PIXEL             │
  │      ██  ██    ██  ██        │ FASE:      Beta (Fase 2: Comportamiento)│
  │      ████████████████        │ HP:        100% Click-Through          │
  │      ████  ████  ████        │ RENDIMIENTO: 20 FPS (5 FPS durmiendo)  │
  │       ▀████████████▀         │ CONSUMO:   0.1% ~ 1.0% CPU en reposo   │
  │         ▀▀▀▀▀▀▀▀▀▀           │ HÁBITAT:   Barra inferior / Overlay    │
  │          █        █          │ COMPAÑERO: Ideal para programadores    │
  └──────────────────────────────┴────────────────────────────────────────┘
```

### ✨ Formas / Paletas de Color (Variantes Shiny)
Al hacer clic o elegir en el menú de la bandeja, Maskot alterna entre 4 colores corporales inspirados en los cartuchos clásicos:

| Variante | Tono | Elemento / Vibra |
|:---:|:---:|:---|
| 🟧 **Fuego (Por defecto)** | `(0.95, 0.58, 0.18)` | Cálido, activo y enérgico |
| 🟩 **Hoja / Menta** | `(0.22, 0.72, 0.62)` | Fresco, relajante y concentrado |
| 🟪 **Psíquico / Amatista** | `(0.62, 0.42, 0.86)` | Misterioso, nocturno y hacker |
| 🌸 **Hada / Rubí** | `(0.92, 0.50, 0.70)` | Dulce, amigable y sociable |

---

## 🎮 Características del Juego

- 🪟 **Capa Fantasma (Click-Through Real):** La ventana es 100% transparente. El cursor del ratón atraviesa todo el lienzo libre (`Gdk.Surface.set_input_region`), interactuando únicamente cuando tocas al sprite o a su globo de diálogo.
- 🎭 **Comportamiento Autónomo:** Sistema de rutinas con pesos probabilísticos: pasea, programa en su laptop, lee en una banca, duerme siestas o pide un café.
- 🍅 **Poké-Pomodoro Integrado:** Temporizadores 25/5, 45/10 y 50/10. La mascota coordina sus actividades según estés en bloque de trabajo o de descanso.
- 🧘 **Pausa Activa (Salud del Entrenador):** Tras 50 minutos continuos de uso, inicia una cuenta regresiva (3, 2, 1) y realiza un estiramiento guiado de 6 segundos.
- 💬 **Globo de Diálogo Dinámico:** Renderizado en Cairo con rabito direccional, sombra y desvanecido; la región de entrada se expande dinámicamente para permitir interacción con el mensaje.
- 🛎️ **Bandeja de Estado (DBus StatusNotifierItem):** Menú nativo en el panel del sistema sin depender de librerías obsoletas de GTK3.
- ⚡ **API HTTP Local (`127.0.0.1:7777`):** Controla a Maskot vía `curl` o scripts bash desde cualquier terminal.
- 🍃 **Ahorro de Batería Legendario:** 20 FPS en actividad normal y **5 FPS durante la siesta**, consumiendo casi 0% de CPU.

---

## ⚔️ Lista de Movimientos (Moveset & Rutinas)

Maskot decide de forma autónoma qué hacer cada 20–40 segundos evaluando pesos de probabilidad (priorizando las actividades tranquilas):

```text
  ╔═════════════════════════════════════════════════════════════════════════════╗
  ║                              LISTA DE ACCIONES                              ║
  ╠═════════════════════════════════════════════════════════════════════════════╣
  ║  [1] PASEAR         (Movimiento por la pantalla buscando un nuevo rincón)   ║
  ║  [2] SIESTA         (Cierra los ojos, baja a 5 FPS y emite "Zzz")           ║
  ║  [3] LEER BANCA     (Coloca una banca y saca su libro de aventuras)         ║
  ║  [4] ECHAR CÓDIGO   (Despliega su mini laptop y teclea a la par tuya)       ║
  ║  [5] CAFÉ BREAK     (Toma una taza humeante en los descansos del Pomodoro)  ║
  ║  [!] SALTO AMISTOSO (¡Hazle click encima y reaccionará saltando!)           ║
  ╚═════════════════════════════════════════════════════════════════════════════╝
```

### 🧠 Primitivas del Motor de Rutinas (`rutinas.py`)
Cada rutina se ensambla con una secuencia de micro-acciones:

| Primitiva | Función |
|---|---|
| `ir_a(x)` | Desplaza al sprite a la coordenada `x` (`None` para destino aleatorio). |
| `decir(texto, ms)` | Despliega un mensaje en el globo de texto durante `ms` milisegundos. |
| `cara(nombre, ms)` | Aplica una expresión facial: `feliz`, `cansado`, `pensar`. |
| `esperar(ms, pose=…)` | Pausa en el lugar con una pose específica (`siesta`, `leer`, `codigo`). |
| `objeto(nombre, x=…)` | Coloca o retira un objeto del escenario (`banca`, `libro`, `taza`, `portatil`). |
| `saltar()` | Efectúa una animación de salto elástico. |
| `fin()` | Concluye la rutina actual y cede el control al bucle aleatorio. |

> [!TIP]
> Si haces clic sobre Maskot en cualquier momento, la rutina actual se cancela de inmediato y el personaje da un salto de saludo.

---

## 🎒 Mochila & Herramientas Clave

### 🍅 Poké-Pomodoro
Controlable desde el menú de la bandeja o la API HTTP.
- **Formatos:** `25/5` (clásico), `45/10` (intensivo), `50/10` (sesión extendida).
- **Indicador:** Tiempo restante visible en el menú desplegable y en el tooltip del icono de la bandeja.
- **Sincronización:** Durante la fase de **Trabajo**, Maskot lee o programa; en la fase de **Descanso**, saca su taza de café y te acompaña a despejar la mente.

### 🧘 Pausa Activa (Estiramiento Antifatiga)
- Monitorea el tiempo de uso continuo de la pantalla.
- Al acumular **50 minutos continuos**, lanza un aviso con cuenta atrás (3, 2, 1) y adopta la pose de estiramiento durante 6 segundos.
- Si detecta inactividad (≥ 1 minuto sin usuario), la racha se reinicia automáticamente sin molestar.

### 💾 Memoria de Cartucho (Preferencias)
Maskot guarda tu progreso en `~/.config/mascota/prefs.json`:
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
- `dias_uso`: Medalla que registra los días distintos en los que has entrenado/trabajado junto a tu mascota.

---

## 🕹️ Requisitos de la Consola

- **Python 3** (verificado en 3.14)
- **PyGObject** con **GTK 4** (verificado en 4.22)
- **pycairo**
- **gtk4-layer-shell** (esencial para sesiones Wayland con protocolo `zwlr_layer_shell_v1`)

### 📦 Instalación de Dependencias

```bash
# Arch Linux / CachyOS / Manjaro
sudo pacman -S gtk4-layer-shell python-gobject gtk4 python-cairo

# Debian / Ubuntu (22.04+)
sudo apt update
sudo apt install libgtk4-layer-shell0 python3-gi python3-gi-cairo gir1.2-gtk-4.0

# Fedora
sudo dnf install gtk4-layer-shell python3-gobject gtk4 python3-cairo
```

> [!NOTE]
> En entornos **X11 puros**, `gtk4-layer-shell` no es necesario: el backend X11 interactúa directamente mediante `libX11` (ctypes) y GDK.

---

## 🚀 Insertar Cartucho (Cómo Ejecutar)

El lanzador inteligente [run.sh](file:///home/andrw/mascota/run.sh) detecta tu entorno gráfico, verifica dependencias y gestiona el orden de enlace de librerías (`LD_PRELOAD`):

```bash
# 1. Modo Estándar (Detección automática de Wayland o X11)
./run.sh

# 2. Forzar Backend X11 / XWayland
./run.sh --x11

# 3. Escalar Sprite (Pixel art nítido al doble de tamaño: 8x => 128 px)
./run.sh --scale 8
```

O lanzamiento directo con Python:
```bash
python3 main.py [--x11] [--scale N]
```

---

## 📡 Poké-Comandos (API HTTP Local en `:7777`)

Maskot incorpora un servidor HTTP ultraligero (`http.server` estándar de Python, sin dependencias externas) que escucha exclusivamente en `127.0.0.1:7777`. Viene apagado por defecto y se enciende con un clic en la bandeja (`API local: activar`).

Los comandos `POST` se despachan de forma segura al hilo principal de GTK vía `GLib.idle_add` (retornando `202 Accepted`).

```bash
# Consultar estado global del sistema
curl -s 127.0.0.1:7777/estado | python3 -m json.tool

# Listar catálogo de rutinas disponibles
curl -s 127.0.0.1:7777/rutinas

# Hacer hablar a Maskot (globo con duración personalizada en ms)
curl -s -X POST -d '{"texto": "¡Hola, Entrenador!", "ms": 4000}' 127.0.0.1:7777/decir

# Notificación rápida (1.8 segundos)
curl -s -X POST -d '{"texto": "Build finalizado con éxito ✨"}' 127.0.0.1:7777/aviso

# Forzar una rutina
curl -s -X POST -d '{"nombre": "siesta"}' 127.0.0.1:7777/rutina

# Controlar el Poké-Pomodoro
curl -s -X POST -d '{"accion": "iniciar", "formato": "25/5"}' 127.0.0.1:7777/pomodoro
curl -s -X POST -d '{"accion": "pausar"}' 127.0.0.1:7777/pomodoro
```

### Tabla de Endpoints

| Método | Ruta | Carga Útil (JSON) | Descripción |
|:---:|---|---|---|
| `GET` | `/estado` | — | Snapshot: sprite, rutina, globo, pomodoro, pausa, API, color, días de uso |
| `GET` | `/rutinas` | — | Catálogo completo de rutinas y micro-acciones |
| `POST` | `/aviso` | `{"texto": "..."}` | Globo de advertencia rápido (1.8 s) |
| `POST` | `/decir` | `{"texto": "...", "ms": 3000}` | Muestra texto durante la duración solicitada |
| `POST` | `/rutina` | `{"nombre": "siesta"}` | Interrumpe y ejecuta la rutina pedida |
| `POST` | `/pomodoro` | `{"accion": "iniciar\|pausar\|reanudar\|saltar\|parar", "formato": "..."}` | Control del ciclo Pomodoro |

---

## 🗺️ Mapa de Compatibilidad (Estado de las Rutas)

Pruebas ejecutadas en entorno: **CachyOS + niri (Wayland) + XWayland**.

| Componente / Escenario | Estado | Notas de Verificación |
|---|:---:|---|
| **Wayland + layer-shell** *(Recomendado)* | 🟢 Verificado | Capa `mascota` en `OVERLAY`, teclado `NONE`. Click-through perfecto con `wl_region`. |
| **Wayland sin layer-shell** *(Fallback)* | 🟡 Funcional | Ventana flotante clásica; emite aviso y mantiene `set_input_region`. |
| **X11 / XWayland** | 🟢 Verificado | Shape de entrada recortado al sprite y globo. Inyección de clic XTest probada. |
| **Rutinas, Poses & Objetos** | 🟢 Verificado | Ciclo completo de las 5 rutinas verificado (banca, libro, laptop, café, siesta). |
| **Globo de Texto Cairo** | 🟢 Verificado | Renderizado nítido; el rabito apunta al sprite y su área recibe clicks. |
| **Poké-Pomodoro** | 🟡 Parcial | Estados, fases y timers verificados; pendiente prueba continua desatendida de 50m. |
| **Bandeja de Estado (DBus)** | 🟡 Parcial | Árbol de submenús `GetLayout` y eventos validados vía DBus. |
| **Pausa Activa (Lógica)** | 🟢 Verificado | Máquina de estados validada con detector simulado (50 min → 3,2,1 → estirar). |
| **Pausa Activa (Sensor Real)** | 🔴 Pendiente | Detalles técnicos explicados abajo (auto-test preventivo). |
| **Consumo de Energía & 5 FPS** | 🟢 Verificado | 0–1% CPU medido en reposo; baja instantáneamente a 5 FPS al dormir. |

---

## 🔬 Notas del Laboratorio (Investigación Técnica & Hacks)

### ⚠️ Estado de la Detección de Inactividad en Wayland
La pausa activa necesita conocer si el usuario sigue frente al teclado. A diferencia de X11 (`MIT-SCREEN-SAVER`), en Wayland no existe una llamada global sin permisos especiales.

> [!WARNING]
> **La detección en Wayland se desactiva preventivamente por seguridad.**  
> Al no existir bindings empaquetados de Python para Wayland (`pywayland` / `pywlroots`), la app habla con `libwayland-client 1.26` directamente mediante `ctypes`. El protocolo `ext-idle-notify-v1` versión 2 reordenó los argumentos de la llamada `get_idle_notification` (`nou` en lugar de `oun`). Al realizar el marshalling a bajo nivel en C con `wl_proxy_marshal_array_flags`, libwayland desreferencia punteros de ID que provocan un fallo de segmentación (`SIGSEGV`, código 139).
>
> Para proteger la experiencia de usuario, Maskot incluye un **auto-test en subproceso aislado** (`python3 pausa.py --selftest`): si el detector falla, la app simplemente desactiva la pausa activa e imprime un aviso claro en consola, **sin colgarse ni cerrarse**.
>
> **Soluciones previstas a futuro:**
> 1. Empaquetar un binding nativo real (`python-wayland`).
> 2. Implementar interfaces específicas por DBus según el compositor (`org.gnome.Mutter.IdleMonitor`, etc.).
> 3. Modo alternativo con diálogo interactivo: "¿Sigues ahí, Entrenador?".

### 🪟 Regla de Ventana para Compositor `niri`
En compositores dinámicos basados en scrolls como `niri`, enfocar una ventana flotante transparente puede provocar que el compositor pinte su halo/anillo de foco (*focus-ring* lavanda) detrás de la ventana.

Para solucionarlo, añade esta regla a tu archivo `~/.config/niri/cfg/rules.kdl`:
```kdl
window-rule {
    match title="^Mascota$"
    open-focused false
    focus-ring { off; }
}
```
*(Maskot define su título exactamente como `Mascota`, por lo que la regla es quirúrgica).*

### 🧩 Otras Particularidades del Sistema
- **Orden de Enlace de `gtk4-layer-shell`:** Debe cargarse en memoria antes de `libwayland`. [run.sh](file:///home/andrw/mascota/run.sh) lo soluciona automáticamente aplicando `LD_PRELOAD`.
- **Bandeja sin librerías obsoletas:** No se utiliza `libayatana-appindicator` (vinculada al runtime de GTK3 incompatible con GTK4). En su lugar, [tray.py](file:///home/andrw/mascota/tray.py) implementa el protocolo StatusNotifierItem nativamente mediante llamadas DBus con `Gio`.
- **Tipografía "Toy" de Cairo:** Los globos utilizan la API tipográfica simplificada de Cairo para mantener cero dependencias pesadas de Pango.

---

## 💾 Estructura del Cartucho (Arquitectura)

```text
mascota/
├── main.py              # Bucle principal, renderizado Cairo, coordinación y eventos
├── rutinas.py           # Motor secuencial de acciones y catálogo de las 5 rutinas
├── objetos.py           # Sprites pixel art de objetos (banca, libro, portátil, taza)
├── globo.py             # Globo de texto Cairo con rabito direccional y sombra
├── pomodoro.py          # Lógica del temporizador Pomodoro (25/5, 45/10, 50/10)
├── pausa.py             # Máquina de estados de pausa activa y auto-test en Wayland
├── api.py               # Servidor HTTP local REST (127.0.0.1:7777) sin dependencias
├── preferencias.py      # Persistencia en disco (~/.config/mascota/prefs.json)
├── sprite.py            # Definición de grilla 16x16, paletas de color, poses y caras
├── tray.py              # Icono y menú en la bandeja del sistema vía DBus puro
├── run.sh               # Lanzador con detección de entorno y comprobación de libs
└── backends/
    ├── __init__.py      # Selector dinámico de backend
    ├── base.py          # Máscaras de entrada (set_input_region) con GDK
    ├── wayland.py       # Integración con gtk4-layer-shell y modo fallback
    └── x11.py           # Ventana EWMH (DOCK/ABOVE) y posicionamiento XLib
```

---

## 🏆 Salón de la Fama (Créditos & Licencia)

Este proyecto es una **implementación original e independiente para Linux** escrita en Python y GTK4. 

Inspirado en el concepto de [alecap92/maskot-mac](https://github.com/alecap92/maskot-mac) (mascota de escritorio para macOS escrita en Swift).
- **No es un fork:** No comparte base de código ni dependencias; la arquitectura, backends gráficos de Wayland/X11, rutinas y motor HTTP han sido diseñados desde cero para el ecosistema Linux.
- Si en el futuro se incorpora arte o recursos directos de dicho proyecto, se preservará la correspondiente licencia MIT y atribución de autoría.

---

<div align="center">

**¿Listo para tu aventura? ¡Ejecuta `./run.sh` y que empiece la jornada de código!**  
*Hecho con ☕, píxeles y amor por el software libre.*

</div>
