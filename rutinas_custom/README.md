# Rutinas personalizadas (JSON)

Pon tus rutinas en esta carpeta como archivos `*.json` y Maskot las carga
al arrancar, junto con las de `~/.config/mascota/rutinas/*.json`. No hace
falta tocar `rutinas.py` ni saber Python.

## Formato

```json
{
  "nombre": "saludo_ejemplo",
  "titulo": "Saludo de ejemplo",
  "peso": 1,
  "solo_fases": null,
  "pasos": [
    {"tipo": "decir", "texto": "¡Hola! Soy una rutina personalizada", "ms": 3000},
    {"tipo": "cara", "nombre": "feliz", "ms": 2000},
    {"tipo": "saltar"}
  ]
}
```

- `nombre`: alfanumérico, `_` o `-`. No puede repetir el de una rutina
  integrada (`pasear`, `siesta`, `bailar`…): las integradas siempre ganan.
- `titulo`: lo que se ve en el menú de la bandeja.
- `peso`: probabilidad relativa (como en las integradas). `0` = nunca sale
  al azar, solo se puede lanzar desde la API o el menú.
- `solo_fases`: `null` (siempre), `"trabajo"` o `"descanso"`.
- `pasos`: lista no vacía con las primitivas del motor (ver `rutinas.py`):

| Tipo | Campos |
|---|---|
| `ir_a` | `x` (entero o `null` = al azar), `ms`, `al_llegar` |
| `decir` | `texto`, `ms` |
| `cara` | `nombre`: `feliz` / `cansado` / `pensar`, `ms` |
| `esperar` | `ms`, `pose`: `siesta` / `leer` / `codigo` / `regar` / `respirar` / `meditar` o `null`, `texto` |
| `objeto` | `nombre`: `banca`, `libro`, `taza`, `portatil`, `papelera`, `hoja`, `regadera`, `croissant`, `pelota`, `escoba`, `esterilla`, `planta_*` o `null` (quita todos), `x`, `y` |
| `quitar` | `nombre` |
| `cuenta_atras` | `n`, `ms`, `texto` (con `{n}`), `duracion` |
| `saltar` | — |
| `fin` | — |

## Ejemplo

`ejemplo-saludo.json` es una rutina válida y se carga al arrancar. Cópiala
como punto de partida. Un archivo inválido se ignora y se avisa por consola;
nunca tumba la mascota.

Puedes probar una rutina custom sin esperar al azar:

```bash
curl -d '{"nombre": "saludo_ejemplo"}' 127.0.0.1:7777/rutina
```
