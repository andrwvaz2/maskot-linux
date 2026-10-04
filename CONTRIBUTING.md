# Guía de Contribución para Maskot 🐾

¡Gracias por tu interés en colaborar con **Maskot para Linux**! Toda aportación, desde la corrección de un bug o reporte de compatibilidad hasta la creación de un nuevo personaje en pixel art, es sumamente apreciada.

---

## 🛠️ Entorno de Desarrollo

### 1. Clonar el repositorio
```bash
git clone https://github.com/andrwvaz2/maskot-linux.git
cd maskot-linux
```

### 2. Dependencias del sistema
Asegúrate de contar con Python 3.10+, PyGObject (GTK4), Cairo y dependencias según tu distribución:
- **Arch Linux / CachyOS:**
  ```bash
  sudo pacman -S python-gobject gtk4 cairo gtk4-layer-shell
  ```
- **Debian / Ubuntu:**
  ```bash
  sudo apt install python3-gi gir1.2-gtk-4.0 python3-cairo libgtk4-layer-shell0
  ```
- **Fedora:**
  ```bash
  sudo dnf install python3-gobject gtk4 cairo-devel gtk4-layer-shell
  ```

### 3. Ejecutar en modo desarrollo
Lanza la aplicación directamente desde la raíz del proyecto:
```bash
./run.sh
```

Para forzar la prueba de una rutina o pose específica en bucle:
```bash
MASKOT_DEMO=matica:loop python3 main.py
```

---

## 📂 Arquitectura del Proyecto

```text
mascota/
├── main.py              # Bucle principal, ventana GTK4, temporizadores y eventos
├── personajes.py        # Catálogo y definiciones de sprites de personajes (16x16)
├── rutinas.py           # Motor de micro-acciones y comportamientos autónomos
├── sprite.py            # Motor de renderizado vectorial/pixel art con Cairo
├── objetos.py           # Objetos del escenario (laptop, maceta, banca, etc.)
├── pausa.py             # Módulo de Pausa Activa y estiramiento postural
├── pomodoro.py          # Módulo de temporizador Pomodoro
├── api.py               # Servidor HTTP local (127.0.0.1:7777)
├── tray.py              # Icono de bandeja del sistema DBus (StatusNotifierItem)
└── backends/            # Capas de compatibilidad Wayland (layer-shell) y X11 (EWMH)
```

---

## 🎨 Creación de Nuevos Personajes o Sprites

Si deseas diseñar un nuevo personaje o accesorio:
- Los sprites base están diseñados en una cuadrícula de **16×16 píxeles** (o proporciones equivalentes).
- Mantén la coherencia visual y paleta con los personajes existentes (`personajes.py`).
- Poses estándar: reposo, parpadeo, caminar (frames 1 y 2), siesta, lectura, laptop, café y estiramiento.

---

## 🌿 Flujo de Trabajo para Pull Requests

1. Haz un **Fork** del repositorio.
2. Crea una rama descriptiva para tu cambio:
   ```bash
   git checkout -b feat/nuevo-personaje
   # o
   git checkout -b fix/compositor-wayland
   ```
3. Realiza tus modificaciones cuidando el estilo del código en Python.
4. Prueba que la aplicación funcione y cierre limpiamente:
   ```bash
   python3 main.py
   ```
5. Haz commit con mensajes claros:
   ```bash
   git commit -m "feat(personajes): agregar nuevo personaje X"
   ```
6. Sube tu rama y abre un **Pull Request** hacia la rama `main` explicando tus cambios.

---

## 💡 Sugerencias y Reportes de Bugs
Si encuentras un error o quieres discutir una nueva funcionalidad antes de programarla, abre un [Issue en GitHub](https://github.com/andrwvaz2/maskot-linux/issues).
