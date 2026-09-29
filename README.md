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

## 📟 Panel de Control Retro & Especificaciones

```text
  ▼ STATS & DASHBOARD ▼
  ┌──────────────────────────────┬────────────────────────────────────────┐
  │         ▄▄▄▄▄▄▄▄▄▄           │ PERSONAJE:   Maskot                    │
  │       ▄████████████▄         │ ESPECIE:     Mascota de Escritorio     │
  │      ████████████████        │ ESTADO:      Beta (Fase 2)             │
  │      ██  ██    ██  ██        │ CLICK-THROUGH: 100% Nativo             │
  │      ████████████████        │ MOTOR:       Python 3 + GTK4 + Cairo   │
  │      ████  ████  ████        │ FPS ACTIVO:  20 FPS                    │
  │       ▀████████████▀         │ FPS SIESTA:  5 FPS (Ahorro de batería) │
  │         ▀▀▀▀▀▀▀▀▀▀           │ CONSUMO CPU: 0.1% ~ 1.0% en reposo     │
  │          █        █          │ DISPLAY:     Wayland (Layer-Shell) / X11│
  └──────────────────────────────┴────────────────────────────────────────┘
```

### 🎨 Paletas de Color Intercambiables
Al hacer clic sobre el personaje o desde el menú de la bandeja, Maskot alterna entre 4 paletas clásicas:

| Paleta | Tono RGB | Descripción |
|:---:|:---:|:---|
| 🟧 **Ámbar / Naranja (Default)** | `(0.95, 0.58, 0.18)` | Cálido y enérgico |
| 🟩 **Menta / Turquesa** | `(0.22, 0.72, 0.62)` | Relajante y fresco |
| 🟪 **Amatista / Violeta** | `(0.62, 0.42, 0.86)` | Estilo nocturno y synthwave |
| 🌸 **Rosa Pastel** | `(0.92, 0.50, 0.70)` | Suave y minimalista |

---

## ⚡ Características Principales

- 🪟 **Ventana Transparente con Click-Through Real:** La ventana flota en pantalla sin marcos ni fondo. El puntero del ratón atraviesa todo el espacio vacío (`Gdk.Surface.set_input_region`), interactuando únicamente cuando haces clic sobre el sprite o sobre su globo de diálogo.
- 🤖 **Rutinas Autónomas Dinámicas:** Motor con pesos probabilísticos que decide qué hacer cada 20–40 segundos (pasear, escribir código en su laptop, leer en una banca, dormir siestas o tomar un café).
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
  ║  • SALTO REACTIVO: ¡Hazle clic en cualquier momento para saludar!           ║
  ╚═════════════════════════════════════════════════════════════════════════════╝
```

### Primitivas del Motor (`rutinas.py`)

| Acción | Efecto |
|---|---|
| `ir_a(x)` | Desplaza el sprite a la posición horizontal `x` (`None` para destino aleatorio). |
| `decir(texto, ms)` | Muestra un texto en el globo de diálogo durante `ms` milisegundos. |
| `cara(nombre, ms)` | Cambia la expresión del rostro: `feliz`, `cansado`, `pensar`. |
| `esperar(ms, pose=…)` | Pausa en el lugar con una pose (`siesta`, `leer`, `codigo`). |
| `objeto(nombre, x=…)` | Coloca o retira un elemento del escenario (`banca`, `libro`, `taza`, `portatil`). |
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
- `dias_uso`: Contador de días naturales en los que has utilizado la app.

---

## 💻 Requisitos del Sistema

- **Python 3** (verificado en 3.14)
- **PyGObject** con **GTK 4** (verificado en 4.22)
- **pycairo**
- **gtk4-layer-shell** (requerido para Wayland mediante el protocolo `zwlr_layer_shell_v1`)

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
> En sesiones **X11**, no es necesario `gtk4-layer-shell`: el backend X11 interactúa directamente mediante `libX11` (ctypes) y GDK.

---

## 🚀 Inicio Rápido (Cómo Ejecutar)

El lanzador [run.sh](file:///home/andrw/mascota/run.sh) detecta el entorno de pantalla, verifica librerías y configura `LD_PRELOAD` automáticamente para asegurar el orden de enlace:

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
python3 main.py [--x11] [--scale N]
```

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
```

### Tabla de Endpoints

| Método | Endpoint | Cuerpo JSON | Descripción |
|:---:|---|---|---|
| `GET` | `/estado` | — | Snapshot del estado: sprite, rutina, globo, pomodoro, pausa, color y días de uso |
| `GET` | `/rutinas` | — | Catálogo de rutinas y micro-acciones |
| `POST` | `/aviso` | `{"texto": "..."}` | Globo rápido de advertencia (1.8 s) |
| `POST` | `/decir` | `{"texto": "...", "ms": 3000}` | Mensaje con duración específica en ms |
| `POST` | `/rutina` | `{"nombre": "siesta"}` | Interrumpe y ejecuta la rutina indicada |
| `POST` | `/pomodoro` | `{"accion": "...", "formato": "..."}` | Iniciar, pausar, reanudar, saltar o parar el Pomodoro |

---

## 🗺️ Matriz de Compatibilidad

Verificado en: **CachyOS + niri (Wayland) + XWayland**.

| Entorno / Componente | Estado | Detalle de Verificación |
|---|:---:|---|
| **Wayland + layer-shell** *(Recomendado)* | 🟢 Verificado | Capa `mascota` en `OVERLAY`, teclado `NONE`. Click-through fluido con `wl_region`. |
| **Wayland sin layer-shell** *(Fallback)* | 🟡 Funcional | Modo ventana flotante; avisa en consola y mantiene `set_input_region`. |
| **X11 / XWayland** | 🟢 Verificado | Shape recortado al sprite y globo. Inyección de clic XTest verificada. |
| **Rutinas y Objetos** | 🟢 Verificado | Las 5 rutinas completan su ciclo (banca, libro, laptop, taza, siesta). |
| **Globo de Diálogo** | 🟢 Verificado | Renderizado Cairo nítido con sombra y rabito direccional. |
| **Temporizador Pomodoro** | 🟡 Parcial | Estados, cambios de fase y avisos probados; falta prueba continua de 50 min. |
| **Bandeja de Estado (DBus)** | 🟡 Parcial | Árbol de submenús `GetLayout` y eventos validados vía DBus. |
| **Pausa Activa (Lógica)** | 🟢 Verificado | Máquina de estados validada con detector simulado (50 min → 3,2,1 → estirar). |
| **Pausa Activa (Sensor Real)** | 🔴 Pendiente | Detalles técnicos explicados en las notas de desarrollo. |
| **Consumo a 5 FPS (Siesta)** | 🟢 Verificado | 0–1% CPU medido en reposo con reprogramación dinámica de FPS. |

---

## 🔬 Notas de Desarrollo & Hacks del Sistema

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
├── rutinas.py           # Motor de micro-acciones y catálogo de las 5 rutinas
├── objetos.py           # Sprites pixel art de objetos (banca, libro, portátil, taza)
├── globo.py             # Globo de texto Cairo con rabito direccional y sombra
├── pomodoro.py          # Lógica del temporizador Pomodoro (25/5, 45/10, 50/10)
├── pausa.py             # Máquina de estados de pausa activa y auto-test en Wayland
├── api.py               # Servidor HTTP local REST (127.0.0.1:7777) sin dependencias
├── preferencias.py      # Persistencia en disco (~/.config/mascota/prefs.json)
├── sprite.py            # Grilla pixel art 16x16, paletas de color, poses y caras
├── tray.py              # Icono y menú en la bandeja del sistema vía DBus puro
├── run.sh               # Lanzador con detección de entorno y comprobación de libs
└── backends/
    ├── __init__.py      # Selector dinámico de backend
    ├── base.py          # Regiones de click-through (set_input_region) con GDK
    ├── wayland.py       # Integración con gtk4-layer-shell y modo fallback
    └── x11.py           # Ventana EWMH (DOCK/ABOVE) y posicionamiento XLib
```

---

## 🏆 Créditos & Atribución

Este proyecto es una **implementación original e independiente para Linux** escrita en Python y GTK4.

Inspirado en la idea de [alecap92/maskot-mac](https://github.com/alecap92/maskot-mac) (mascota para macOS en Swift).
- **No es un fork:** No comparte código ni dependencias; la arquitectura, backends de renderizado Wayland/X11, rutinas y motor HTTP han sido programados desde cero para el ecosistema Linux.
- Si en el futuro se reutiliza código o arte de dicho proyecto, se mantendrá su licencia MIT y la atribución correspondiente.

---

<div align="center">

**¿Listo para probarlo? ¡Lanza `./run.sh` en tu terminal!**  
*Desarrollado con ☕, píxeles y cariño por el software libre.*

</div>
