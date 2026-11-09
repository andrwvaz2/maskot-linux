# CHANGELOG — Maskot

## v0.3.0-beta — Fase 3 (2026-11-09)

### Personajes y rutinas

- **Pancito, el croissant dorado** (personaje 10): cuerpo 16x16 con paleta
  `#E8A93D` / `#FFF2DD`, caras feliz/cansado/pensar y patas en la fila 15.
- **4 objetos nuevos** en `objetos.py`: `croissant` (10x6), `pelota`
  (8x8), `escoba` (8x10) y `esterilla` (12x4). Paleta ampliada con `E`/`e`
  (dorado).
- **6 rutinas nuevas** (8 -> 14): `bailar`, `merienda` (comer croissant),
  `jugar_pelota`, `limpiar`, `meditar` (nueva pose, ojos cerrados) y
  `saludo_hora` (según la hora del día). `elegir()` ahora incluye
  `meditar` en trabajo y `bailar`/`jugar_pelota`/`merienda` en descanso,
  y respeta `solo_fases` en las rutinas custom.

### Rutinas y personajes personalizados (JSON)

- Nuevo `rutinas_custom.py`: carga `*.json` de `./rutinas_custom/` y de
  `~/.config/mascota/rutinas/`, con validación estricta y sin crashear
  nunca. Ejemplo válido: `rutinas_custom/ejemplo-saludo.json`.
- Nuevo `personajes_custom.py`: carga `*.json` de
  `./personajes_custom/` y de `~/.config/mascota/personajes/`, validando
  16 filas x 16 caracteres y paleta hex. Ejemplo válido:
  `personajes_custom/ejemplo-gato.json` (Mishi).
- Las integradas nunca se pisan: un JSON no puede sobrescribir `pasear`,
  `tux` ni `pancito`.

### Logros, racha y reacciones al sistema

- Nuevo `logros.py` (sin GTK): 7 logros — primera semana, racha de 3 y 7
  días, 10 y 50 pomodoros, 50 rutinas y jardinero (regar 5 veces).
- `preferencias.py`: nuevas claves `pomodoros`, `rutinas_completadas`,
  `matica_completadas`, `logros`, `racha_dias`, `ultimo_dia_racha`,
  `sonido` y `musica_baile`. `marcar_dia_de_uso()` calcula la racha.
- Nuevo `sistema.py` (stdlib): `bateria()` (`/sys/class/power_supply`),
  `musica_actual()` (`playerctl`/MPRIS) y `tocar_nota()` (WAV sine con
  `paplay`/`aplay`/`ffplay`). Nada crashea si falta algo.
- `main.py`: al terminar una rutina se registra y se anuncian los logros
  nuevos en el globo (con sonido si está activado); al completar un ciclo
  de pomodoro también. Chequeo de batería (<20%) y música (baila en
  descanso, una vez por canción) una vez por minuto. Menú reorganizado:
  rutinas en 100+, personajes en 200+, API 300, pausa 301, logros 302,
  sonido 303. `estado_actual()` incluye `logros` y `sistema`.
- `api.py`: nuevo `GET /logros`.

### Pausa activa en Wayland

- Nuevo `DBusIdle` en `pausa.py`: `org.gnome.Mutter.IdleMonitor`
  (`GetIdletime()`) vía Gio, con import perezoso. Se prueba antes que
  `ext-idle-notify-v1` en Wayland; si no está, cae al de antes. X11 no
  cambia. KDE sigue pendiente.

### Docs

- README actualizado a v0.3.0-beta Fase 3: 10 personajes, 14 rutinas,
  secciones de JSON custom, logros, reacciones al sistema y pausa por DBus.
- Nuevos `ROADMAP.md` y `CHANGELOG.md`.

## v0.2.0-beta — Fase 2

- Ventana flotante transparente con click-through, 9 personajes, 8
  rutinas, Pomodoro, pausa activa, API HTTP local y preferencias
  persistentes. Ver README para el detalle.
