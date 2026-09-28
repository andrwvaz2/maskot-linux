"""Preferencias en `~/.config/mascota/prefs.json`.

Guarda lo mínimo persistente: el personaje elegido (color del cuerpo) y el
contador de días de uso. Todo lo demás (formato de pomodoro, si la pausa
activa está activa…) también se guarda aquí, pero es opcional: si el fichero se
corrompe se avisa y se arranca con los valores por defecto, sin crashear.
"""

from __future__ import annotations

import datetime
import json
import os

RUTA_POR_DEFECTO = os.path.join(
    os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
    "mascota",
    "prefs.json",
)

# Personaje -> color del cuerpo. Los nombres coinciden con BODY_COLORS de
# sprite.py en orden: naranja, verde, violeta, rosa.
PERSONAJES = ("naranja", "verde", "violeta", "rosa")

DEFAULTS = {
    "personaje": "naranja",
    "dias_uso": 0,
    "ultimo_dia": "",
    "formato_pomodoro": "25/5",
    "pausa_activa": True,
    "api_puerto": 7777,
}


class Preferencias:
    """Carga/guarda el fichero de preferencias y cuenta los días de uso."""

    def __init__(self, ruta=RUTA_POR_DEFECTO):
        self.ruta = ruta
        self.datos = dict(DEFAULTS)
        self.datos.update(self._leer())
        self.marcar_dia_de_uso()

    # -- E/S ----------------------------------------------------------------

    def _leer(self):
        try:
            with open(self.ruta, "r", encoding="utf-8") as fh:
                datos = json.load(fh)
        except FileNotFoundError:
            return {}
        except (OSError, ValueError) as exc:
            print(f"[preferencias] no se pudo leer {self.ruta}: {exc}; "
                  "se usan los valores por defecto")
            return {}
        if not isinstance(datos, dict):
            print("[preferencias] el fichero no es un objeto JSON; se ignora")
            return {}
        return {k: v for k, v in datos.items() if k in DEFAULTS}

    def guardar(self):
        try:
            os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
            tmp = f"{self.ruta}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self.datos, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            os.replace(tmp, self.ruta)
        except OSError as exc:
            print(f"[preferencias] no se pudo guardar {self.ruta}: {exc}")

    # -- valores ------------------------------------------------------------

    def get(self, clave, por_defecto=None):
        return self.datos.get(clave, por_defecto if por_defecto is not None
                               else DEFAULTS.get(clave))

    def set(self, clave, valor):
        self.datos[clave] = valor

    @property
    def personaje(self):
        return self.get("personaje")

    @personaje.setter
    def personaje(self, nombre):
        if nombre in PERSONAJES:
            self.datos["personaje"] = nombre

    @property
    def dias_uso(self):
        return int(self.get("dias_uso") or 0)

    def marcar_dia_de_uso(self):
        """Suma 1 al contador si hoy no se había contado ya."""
        hoy = datetime.date.today().isoformat()
        if self.get("ultimo_dia") == hoy:
            return False
        self.datos["dias_uso"] = self.dias_uso + 1
        self.datos["ultimo_dia"] = hoy
        self.guardar()
        return True
