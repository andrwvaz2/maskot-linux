"""Logros y racha.

Todo con datos dict, sin GTK: las funciones aceptan un dict o un objeto
``Preferencias`` (con ``get``/``set``/``guardar``). No tocan la pantalla;
quien las llama decide cómo anunciar un logro nuevo (globo + sonido).
"""

from __future__ import annotations

LOGROS = {
    "primera_semana": {
        "titulo": "Primera semana",
        "desc": "Usa Maskot 7 días",
        "condicion": lambda s: s.get("dias_uso", 0) >= 7,
    },
    "racha_3": {
        "titulo": "Racha de 3 días",
        "desc": "Usa Maskot 3 días seguidos",
        "condicion": lambda s: s.get("racha_dias", 0) >= 3,
    },
    "racha_7": {
        "titulo": "Racha de 7 días",
        "desc": "Usa Maskot 7 días seguidos",
        "condicion": lambda s: s.get("racha_dias", 0) >= 7,
    },
    "pomodoro_10": {
        "titulo": "10 pomodoros",
        "desc": "Completa 10 ciclos de pomodoro",
        "condicion": lambda s: s.get("pomodoros", 0) >= 10,
    },
    "pomodoro_50": {
        "titulo": "50 pomodoros",
        "desc": "Completa 50 ciclos de pomodoro",
        "condicion": lambda s: s.get("pomodoros", 0) >= 50,
    },
    "rutinas_50": {
        "titulo": "50 rutinas",
        "desc": "Completa 50 rutinas",
        "condicion": lambda s: s.get("rutinas_completadas", 0) >= 50,
    },
    "jardinero": {
        "titulo": "Jardinero",
        "desc": "Riega la plantita 5 veces",
        "condicion": lambda s: s.get("matica_completadas", 0) >= 5,
    },
}


def _stats(prefs):
    """Estadísticas como dict, venga de donde venga ``prefs``."""
    claves = ("dias_uso", "racha_dias", "pomodoros", "rutinas_completadas",
              "matica_completadas", "logros")
    if isinstance(prefs, dict):
        return {k: prefs.get(k, 0 if k != "logros" else []) for k in claves}
    get = getattr(prefs, "get", None)
    if callable(get):
        return {k: get(k, 0 if k != "logros" else []) for k in claves}
    datos = getattr(prefs, "datos", {}) or {}
    return {k: datos.get(k, 0 if k != "logros" else []) for k in claves}


def _get(prefs, clave, defecto=None):
    if isinstance(prefs, dict):
        return prefs.get(clave, defecto)
    get = getattr(prefs, "get", None)
    if callable(get):
        return get(clave, defecto)
    return getattr(prefs, "datos", {}).get(clave, defecto)


def _set(prefs, clave, valor):
    if isinstance(prefs, dict):
        prefs[clave] = valor
        return
    setter = getattr(prefs, "set", None)
    if callable(setter):
        setter(clave, valor)
        return
    datos = getattr(prefs, "datos", None)
    if isinstance(datos, dict):
        datos[clave] = valor


def _guardar(prefs):
    guardar = getattr(prefs, "guardar", None)
    if callable(guardar):
        try:
            guardar()
        except Exception:  # noqa: BLE001
            pass


def desbloqueados(prefs):
    """IDs de logros cuya condición ya se cumple."""
    stats = _stats(prefs)
    return [lid for lid, info in LOGROS.items()
            if info["condicion"](stats)]


def comprobar_nuevos(prefs):
    """Logros recién desbloqueados (y los guarda en ``prefs``)."""
    ya = list(_get(prefs, "logros", []) or [])
    nuevos = [lid for lid in desbloqueados(prefs) if lid not in ya]
    if nuevos:
        _set(prefs, "logros", ya + nuevos)
        _guardar(prefs)
    return nuevos


def registrar_pomodoro(prefs):
    """Suma un ciclo de pomodoro y devuelve los logros nuevos."""
    _set(prefs, "pomodoros", int(_get(prefs, "pomodoros", 0) or 0) + 1)
    _guardar(prefs)
    return comprobar_nuevos(prefs)


def registrar_rutina(prefs, nombre):
    """Suma una rutina completada y devuelve los logros nuevos."""
    _set(prefs, "rutinas_completadas",
         int(_get(prefs, "rutinas_completadas", 0) or 0) + 1)
    if nombre == "matica":
        _set(prefs, "matica_completadas",
             int(_get(prefs, "matica_completadas", 0) or 0) + 1)
    _guardar(prefs)
    return comprobar_nuevos(prefs)
