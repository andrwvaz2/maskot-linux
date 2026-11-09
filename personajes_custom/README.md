# Personajes personalizados (JSON)

Pon tus personajes en esta carpeta como archivos `*.json` y Maskot los
carga al arrancar, junto con los de `~/.config/mascota/personajes/*.json`.
No hace falta tocar `personajes.py` ni saber Python.

## Formato

```json
{
  "id": "gato",
  "nombre": "Mishi",
  "desc": "Un gato naranja curioso",
  "paleta": {"c": "#E07A3F", "C": "#FFF2DD", "1": "#F58594",
             "2": "#B45309", "O": "#111827"},
  "cuerpo": ["................", "... 16 filas de 16 caracteres ..."],
  "cara_neutro": {"5": ".OccC5oCC5oCccO.", "6": ".OccCooCCooCccO."},
  "caras": {
    "feliz": {"5": "...", "6": "..."},
    "cansado": {"5": "..."},
    "pensar": {"5": "..."}
  },
  "patas_fila": 15,
  "paso1": [3, 4],
  "paso2": [10, 11]
}
```

- `id`: alfanumérico, `_` o `-`. No puede repetir el de un personaje
  integrado (`tux`, `pancito`…): los integrados siempre ganan.
- `paleta`: letras de un carácter -> color hex `#RRGGBB`. Esas letras son
  las que puedes usar en `cuerpo` y en las caras.
- `cuerpo`: exactamente 16 filas de 16 caracteres. `.` es transparente.
  Además de tu paleta, puedes usar las tintas base: `o` (ojo), `5`
  (brillo blanco), `r` (rubor), `O`, `C`, `1`..`5`, `K`, `B`, `P`, `Z`.
- `cara_neutro`: obligatoria. Filas (0-15) con cadenas de 16 caracteres;
  `.` conserva el cuerpo en esa posición. Los ojos van en las filas 5-6
  en la mayoría de personajes.
- `caras`: `feliz`, `cansado` y `pensar`, con el mismo formato. Si falta
  una, se usa la neutra.
- `patas_fila`: fila de las patas (normalmente 15).
- `paso1` / `paso2`: columnas de esa fila que se levantan al caminar
  (alternan en los dos cuadros de caminata).

## Ejemplo

`ejemplo-gato.json` es un personaje válido (Mishi, un gato naranja) y se
carga al arrancar. Cópialo como punto de partida. Un archivo inválido se
ignora y se avisa por consola; nunca tumba la mascota.

Para cambiar al personaje desde la terminal (con la API activada):

```bash
curl -d '{"nombre": "gato"}' 127.0.0.1:7777/personaje
```
