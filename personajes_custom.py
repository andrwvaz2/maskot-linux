"""Personajes personalizados en JSON.

Carga ``*.json`` de ``./personajes_custom/`` (en el repo) y de
``~/.config/mascota/personajes/*.json``. Un archivo inválido solo avisa por
consola y se ignora: nunca tumba la mascota.

Formato::

    {
      "id": "gato",
      "nombre": "Mishi",
      "desc": "Un gato naranja curioso",
      "paleta": {"c": "#E07A3F", "C": "#FFF2DD", "1": "#F58594",
                 "2": "#B45309", "O": "#111827"},
      "cuerpo": ["................", ... 16 filas de 16 caracteres ...],
      "cara_neutro": {"5": "...", "6": "..."},
      "caras": {"feliz": {...}, "cansado": {...}, "pensar": {...}},
      "patas_fila": 15,
      "paso1": [3, 4],
      "paso2": [10, 11]
    }

- ``cuerpo``: 16 filas de 16 caracteres. ``.`` es transparente; cada letra
  debe estar en ``paleta`` o ser una tinta base conocida (``o``, ``5``,
  ``r``, ``O``, ``C``, ``1``..``5``, ``K``, ``B``, ``P``, ``Z``…).
- ``cara_neutro`` / ``caras``: filas (0-15) con cadenas de 16 caracteres;
  ``.`` conserva el cuerpo. Las caras son opcionales: si falta una, se usa
  la neutra.
- ``paleta``: letras de un carácter -> color hex ``#RRGGBB``.
"""

from __future__ import annotations

import json
import os
import re

_TINTAS_BASE = set("corgvbsnzpwl kOC12345ZKBP".replace(" ", ""))
_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _validar_filas(filas, que):
    if not isinstance(filas, list) or len(filas) != 16:
        raise ValueError(f"'{que}' debe tener 16 filas")
    for fila in filas:
        if not isinstance(fila, str) or len(fila) != 16:
            raise ValueError(f"'{que}': cada fila debe tener 16 caracteres")
    return tuple(filas)


def _validar_cara(cara, paleta, que):
    if cara is None:
        return {}
    if not isinstance(cara, dict):
        raise ValueError(f"'{que}' debe ser un objeto fila->texto")
    salida = {}
    for fila, texto in cara.items():
        try:
            n = int(fila)
        except (TypeError, ValueError):
            raise ValueError(f"'{que}': la fila {fila!r} no es un número")
        if not 0 <= n <= 15:
            raise ValueError(f"'{que}': la fila {n} está fuera de 0-15")
        if not isinstance(texto, str) or len(texto) != 16:
            raise ValueError(f"'{que}': la fila {n} debe tener 16 caracteres")
        for ch in texto:
            if ch != "." and ch not in paleta and ch not in _TINTAS_BASE:
                raise ValueError(f"'{que}': carácter {ch!r} sin paleta")
        salida[n] = texto
    return salida


def _validar_personaje(datos, ruta):
    from personajes import Personaje, hex_to_rgb

    if not isinstance(datos, dict):
        raise ValueError("el JSON no es un objeto")
    pid = datos.get("id")
    if not isinstance(pid, str) or not _ID_RE.match(pid):
        raise ValueError("'id' debe ser alfanumérico, _ o -")
    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or not nombre:
        raise ValueError("'nombre' debe ser una cadena no vacía")
    desc = datos.get("desc") or nombre
    if not isinstance(desc, str):
        raise ValueError("'desc' debe ser una cadena")
    paleta_raw = datos.get("paleta")
    if not isinstance(paleta_raw, dict) or not paleta_raw:
        raise ValueError("'paleta' debe ser un objeto no vacío")
    paleta = {}
    for letra, color in paleta_raw.items():
        if not isinstance(letra, str) or len(letra) != 1:
            raise ValueError("'paleta': la clave debe ser un carácter")
        if not isinstance(color, str) or not _HEX_RE.match(color):
            raise ValueError(f"'paleta': {color!r} no es #RRGGBB")
        paleta[letra] = hex_to_rgb(color)
    cuerpo = _validar_filas(datos.get("cuerpo"), "cuerpo")
    for fila in cuerpo:
        for ch in fila:
            if ch != "." and ch not in paleta and ch not in _TINTAS_BASE:
                raise ValueError(f"'cuerpo': carácter {ch!r} sin paleta")
    cara_neutro = _validar_cara(datos.get("cara_neutro"), paleta, "cara_neutro")
    if not cara_neutro:
        raise ValueError("'cara_neutro' es obligatoria")
    caras_raw = datos.get("caras") or {}
    if not isinstance(caras_raw, dict):
        raise ValueError("'caras' debe ser un objeto")
    caras = {k: _validar_cara(v, paleta, f"caras.{k}")
             for k, v in caras_raw.items()}
    patas = datos.get("patas_fila", 15)
    if not isinstance(patas, int) or isinstance(patas, bool) or not 0 <= patas <= 15:
        raise ValueError("'patas_fila' debe ser un entero 0-15")
    for clave in ("paso1", "paso2"):
        pasos = datos.get(clave)
        if (not isinstance(pasos, list) or not pasos
                or any(not isinstance(c, int) or isinstance(c, bool)
                       or not 0 <= c <= 15 for c in pasos)):
            raise ValueError(f"'{clave}' debe ser una lista de columnas 0-15")
    return pid, Personaje(
        id=pid, nombre=nombre, desc=desc, paleta_override=paleta,
        cuerpo=cuerpo, cara_neutro=cara_neutro, caras=caras,
        patas_fila=patas, paso1=list(datos["paso1"]),
        paso2=list(datos["paso2"]),
    )


def _directorios():
    base = os.path.dirname(os.path.abspath(__file__))
    config = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return [os.path.join(base, "personajes_custom"),
            os.path.join(config, "mascota", "personajes")]


def cargar_personajes_custom(dirs=None):
    """Carga personajes JSON válidos. Nunca lanza excepciones."""
    resultado = {}
    for directorio in (dirs if dirs is not None else _directorios()):
        try:
            archivos = sorted(os.listdir(directorio))
        except OSError:
            continue
        for archivo in archivos:
            if not archivo.endswith(".json"):
                continue
            ruta = os.path.join(directorio, archivo)
            try:
                with open(ruta, "r", encoding="utf-8") as fh:
                    datos = json.load(fh)
                pid, pj = _validar_personaje(datos, ruta)
            except Exception as exc:  # noqa: BLE001
                print(f"[personajes_custom] se ignora {ruta}: {exc}")
                continue
            if pid in resultado:
                print(f"[personajes_custom] '{pid}' duplicado en {ruta}; "
                      "se queda el primero")
                continue
            resultado[pid] = pj
    return resultado
