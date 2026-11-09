"""Rutinas personalizadas en JSON.

Carga ``*.json`` de ``./rutinas_custom/`` (en el repo) y de
``~/.config/mascota/rutinas/*.json``. Un archivo inválido solo avisa por
consola y se ignora: nunca tumba la mascota.

Formato::

    {
      "nombre": "saludo_ejemplo",
      "titulo": "Saludo de ejemplo",
      "peso": 1,
      "solo_fases": null,        // o "trabajo" | "descanso"
      "pasos": [
        {"tipo": "decir", "texto": "¡Hola!", "ms": 3000},
        {"tipo": "cara", "nombre": "feliz", "ms": 2000},
        {"tipo": "saltar"}
      ]
    }

Tipos de paso (las mismas primitivas de ``rutinas.py``):

- ``ir_a``: {"x": 200 | null, "ms": null, "al_llegar": true}
- ``decir``: {"texto": "...", "ms": 3000}
- ``cara``: {"nombre": "feliz"|"cansado"|"pensar", "ms": 2000}
- ``esperar``: {"ms": 1000, "pose": "siesta"|"leer"|"codigo"|"regar"|
  "respirar"|"meditar"|null, "texto": null}
- ``objeto``: {"nombre": "banca"|"libro"|...|null, "x": null, "y": null}
- ``quitar``: {"nombre": "hoja"}
- ``cuenta_atras``: {"n": 3, "ms": 1000, "texto": "Respira en {n}…",
  "duracion": 900}
- ``saltar``: {}
- ``fin``: {}
"""

from __future__ import annotations

import json
import os
import re

TIPOS_PASO = {
    "ir_a", "decir", "cara", "esperar", "objeto", "quitar",
    "cuenta_atras", "saltar", "fin",
}
POSES_VALIDAS = ("siesta", "leer", "codigo", "regar", "respirar", "meditar")
CARAS_VALIDAS = ("feliz", "cansado", "pensar")
_NOMBRE_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _es_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _validar_paso(paso, ruta):
    """Valida un paso JSON y lo convierte a dict de acción del motor."""
    if not isinstance(paso, dict):
        raise ValueError("el paso no es un objeto")
    tipo = paso.get("tipo")
    if tipo not in TIPOS_PASO:
        raise ValueError(f"tipo de paso desconocido: {tipo!r}")
    if tipo == "ir_a":
        x = paso.get("x")
        if x is not None and not _es_int(x):
            raise ValueError("'x' debe ser entero o null")
        ms = paso.get("ms")
        if ms is not None and not _es_int(ms):
            raise ValueError("'ms' debe ser entero o null")
        return {"tipo": "ir_a", "x": x, "ms": ms,
                "al_llegar": bool(paso.get("al_llegar", False))}
    if tipo == "decir":
        if not isinstance(paso.get("texto"), str) or not paso["texto"]:
            raise ValueError("'texto' debe ser una cadena no vacía")
        ms = paso.get("ms", 3200)
        if not _es_int(ms):
            raise ValueError("'ms' debe ser entero")
        return {"tipo": "decir", "texto": paso["texto"], "ms": ms}
    if tipo == "cara":
        if paso.get("nombre") not in CARAS_VALIDAS:
            raise ValueError(f"'nombre' debe ser una de {CARAS_VALIDAS}")
        ms = paso.get("ms", 2000)
        if not _es_int(ms):
            raise ValueError("'ms' debe ser entero")
        return {"tipo": "cara", "nombre": paso["nombre"], "ms": ms}
    if tipo == "esperar":
        ms = paso.get("ms")
        if not _es_int(ms):
            raise ValueError("'ms' debe ser entero")
        pose = paso.get("pose")
        if pose is not None and pose not in POSES_VALIDAS:
            raise ValueError(f"'pose' debe ser una de {POSES_VALIDAS}")
        texto = paso.get("texto")
        if texto is not None and not isinstance(texto, str):
            raise ValueError("'texto' debe ser cadena o null")
        return {"tipo": "esperar", "ms": ms, "pose": pose, "texto": texto}
    if tipo == "objeto":
        nombre = paso.get("nombre")
        if nombre is not None and not isinstance(nombre, str):
            raise ValueError("'nombre' debe ser cadena o null")
        for clave in ("x", "y"):
            if paso.get(clave) is not None and not _es_int(paso[clave]):
                raise ValueError(f"'{clave}' debe ser entero o null")
        return {"tipo": "objeto", "nombre": nombre,
                "x": paso.get("x"), "y": paso.get("y")}
    if tipo == "quitar":
        if not isinstance(paso.get("nombre"), str):
            raise ValueError("'nombre' debe ser una cadena")
        return {"tipo": "quitar", "nombre": paso["nombre"]}
    if tipo == "cuenta_atras":
        for clave, defecto in (("n", 3), ("ms", 1000), ("duracion", 900)):
            if paso.get(clave, defecto) is not None and not _es_int(paso.get(clave, defecto)):
                raise ValueError(f"'{clave}' debe ser entero")
        texto = paso.get("texto", "Respira en {n}…")
        if not isinstance(texto, str):
            raise ValueError("'texto' debe ser una cadena")
        return {"tipo": "cuenta_atras", "n": paso.get("n", 3),
                "ms": paso.get("ms", 1000), "texto": texto,
                "duracion": paso.get("duracion", 900)}
    # saltar / fin
    return {"tipo": tipo}


def _validar_rutina(datos, ruta):
    if not isinstance(datos, dict):
        raise ValueError("el JSON no es un objeto")
    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or not _NOMBRE_RE.match(nombre):
        raise ValueError("'nombre' debe ser alfanumérico, _ o -")
    titulo = datos.get("titulo") or nombre
    if not isinstance(titulo, str):
        raise ValueError("'titulo' debe ser una cadena")
    peso = datos.get("peso", 1)
    if not isinstance(peso, (int, float)) or isinstance(peso, bool):
        raise ValueError("'peso' debe ser un número")
    solo = datos.get("solo_fases")
    if solo is not None and solo not in ("trabajo", "descanso"):
        raise ValueError("'solo_fases' debe ser null, 'trabajo' o 'descanso'")
    pasos_raw = datos.get("pasos")
    if not isinstance(pasos_raw, list) or not pasos_raw:
        raise ValueError("'pasos' debe ser una lista no vacía")
    pasos = [_validar_paso(p, ruta) for p in pasos_raw]
    return nombre, {
        "peso": peso,
        "titulo": titulo,
        "solo_fases": solo,
        "pasos": lambda rng, _p=tuple(pasos): [dict(p) for p in _p],
    }


def _directorios():
    base = os.path.dirname(os.path.abspath(__file__))
    config = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return [os.path.join(base, "rutinas_custom"),
            os.path.join(config, "mascota", "rutinas")]


def cargar_rutinas_custom(dirs=None):
    """Carga rutinas JSON válidas. Nunca lanza excepciones."""
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
                nombre, info = _validar_rutina(datos, ruta)
            except Exception as exc:  # noqa: BLE001
                print(f"[rutinas_custom] se ignora {ruta}: {exc}")
                continue
            if nombre in resultado:
                print(f"[rutinas_custom] '{nombre}' duplicado en {ruta}; "
                      "se queda el primero")
                continue
            resultado[nombre] = info
    return resultado
