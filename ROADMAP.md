# ROADMAP — Maskot

Qué sigue después de la v0.3.0-beta (Fase 3). Nada de esto está probado ni
prometido: es la lista de trabajo pendiente, en orden aproximado.

## Corto plazo

- **GIF demo en el README**: grabar las rutinas nuevas (bailar, merienda,
  jugar con la pelota, meditar) en acción, en niri, y poner el GIF arriba
  del catálogo de rutinas. Hoy el README no tiene video.
- **Revisión visual en pantalla** de las 6 rutinas nuevas y de Pancito
  (los ciclos ya se verifican sin ventana, pero no se ha visto el pixel
  art en el escritorio).
- **Sonido real con altavoz**: probar `tocar_nota` con `paplay`/`aplay` en
  una máquina con audio; hoy solo se verifica que no crashea sin
  reproductor.
- **Pruebas de la pausa activa por DBus** en una sesión GNOME real
  (`org.gnome.Mutter.IdleMonitor`): hoy solo se verifica que sin sesión
  DBus queda `disponible=False` sin excepciones.

## Compatibilidad (no probado — no tomar como cobertura)

- **Hyprland, Sway, KDE Plasma, XFCE, MATE**: el instalador propone
  reglas, pero ninguna está verificada internamente. Solo niri está
  probado y GNOME (vía XWayland) tiene reporte de comunidad.
- **Pausa activa en KDE**: investigar la ruta DBus de KWin para la
  inactividad. Hoy `DBusIdle` solo implementa Mutter; en KDE cae a
  `ext-idle-notify-v1` si el compositor lo anuncia.
- **GNOME sin XWayland**: el fallback Wayland nativo (ventana normal, sin
  anclar) sigue sin probar.

## Crecimiento del repo

- **Más personajes de la comunidad** en `personajes_custom/`: el formato
  JSON ya está; falta difundirlo y aceptar aportes.
- **Más rutinas de la comunidad** en `rutinas_custom/` (mismo formato).
- **Tests automatizados en CI** (GitHub Actions): hoy los tests son un
  script local (`/tmp/test_maskot_todo.py` en su momento); conviene
  subirlos como `tests/` y correr `py_compile` + el motor sin display en
  cada push.
- **Empaquetado**: Flatpak y/o AUR, para instalar sin clonar el repo.
  Antes hay que resolver las dependencias (GTK4, `gtk4-layer-shell`,
  `playerctl` opcional).

## Ideas (sin compromiso)

- Rutina de "trabajo en equipo": que la mascota reaccione a notificaciones
  del sistema (build terminado, batería, etc.) vía la API `/aviso`.
- Modo "no molestar" por horario (por ejemplo, de noche solo siesta).
- Editor visual de rutinas JSON (una ventanita que genere el JSON).
