"""Pomodoro: bloques de trabajo y descansos.

Formatos soportados: 25/5, 45/10 y 50/10 (trabajo/descanso, en minutos).
El estado es simple: `parado` -> `trabajo` -> `descanso` -> `trabajo`...

La mascota acompaña la fase: en `trabajo` se dedication a programar o leer, y
en `descanso` se toma un café (el motor de rutinas elige la rutina adecuada
mirando la fase).
"""

from __future__ import annotations

FORMATOS = {
    "25/5": (25 * 60 * 1000, 5 * 60 * 1000),
    "45/10": (45 * 60 * 1000, 10 * 60 * 1000),
    "50/10": (50 * 60 * 1000, 10 * 60 * 1000),
}
FORMATO_POR_DEFECTO = "25/5"

FASE_PARADO = "parado"
FASE_TRABAJO = "trabajo"
FASE_DESCANSO = "descanso"


class Pomodoro:
    """Temporizador de pomodoro con avance por reloj (sin hilos)."""

    def __init__(self, formato=FORMATO_POR_DEFECTO, on_cambio=None):
        self.formato = formato if formato in FORMATOS else FORMATO_POR_DEFECTO
        self.fase = FASE_PARADO
        self.restante_ms = 0
        self.ciclos = 0
        self._on_cambio = on_cambio
        self._avisado_cambio_fase = False

    # -- control ------------------------------------------------------------

    def iniciar(self, formato=None):
        if formato is not None:
            self.formato = formato if formato in FORMATOS else self.formato
        trabajo, _ = FORMATOS[self.formato]
        self.fase = FASE_TRABAJO
        self.restante_ms = trabajo
        self.ciclos = 0
        self._avisar()
        return self.fase

    def pausar(self):
        """Pausa el bloque en curso (el formato se conserva)."""
        if self.fase == FASE_PARADO:
            return False
        self._guardado = (self.fase, self.restante_ms)
        self.fase = FASE_PARADO
        self._avisar()
        return True

    def reanudar(self):
        guardado = getattr(self, "_guardado", None)
        if not guardado or self.fase != FASE_PARADO:
            return False
        self.fase, self.restante_ms = guardado
        self._avisar()
        return True

    def saltar(self):
        """Salta a la fase siguiente (trabajo -> descanso -> trabajo)."""
        if self.fase == FASE_PARADO:
            return False
        if self.fase == FASE_TRABAJO:
            self._entrar_descanso()
        else:
            self._entrar_trabajo(contar=False)
        self._avisar()
        return True

    def parar(self):
        self.fase = FASE_PARADO
        self.restante_ms = 0
        self._avisar()
        return True

    # -- reloj ---------------------------------------------------------------

    def tick(self, dt_ms):
        if self.fase == FASE_PARADO or self.restante_ms <= 0:
            return
        self.restante_ms = max(0, self.restante_ms - int(dt_ms))
        if self.restante_ms == 0:
            if self.fase == FASE_TRABAJO:
                self._entrar_descanso()
            else:
                self._entrar_trabajo(contar=True)
            self._avisar()

    def _entrar_trabajo(self, contar=True):
        trabajo, _ = FORMATOS[self.formato]
        self.fase = FASE_TRABAJO
        self.restante_ms = trabajo
        if contar:
            self.ciclos += 1

    def _entrar_descanso(self):
        _, descanso = FORMATOS[self.formato]
        self.fase = FASE_DESCANSO
        self.restante_ms = descanso

    # -- información ---------------------------------------------------------

    @property
    def activo(self):
        return self.fase != FASE_PARADO

    def en_trabajo(self):
        return self.fase == FASE_TRABAJO

    def segundos_restantes(self):
        return int(round(self.restante_ms / 1000.0))

    def reloj(self):
        """Restante como 'mm:ss'."""
        seg = self.segundos_restantes()
        return f"{seg // 60:02d}:{seg % 60:02d}"

    def texto_menu(self):
        if self.fase == FASE_PARADO:
            return f"Pomodoro {self.formato} (parado)"
        return f"Pomodoro {self.fase}: {self.reloj()}"

    def texto_tooltip(self):
        if self.fase == FASE_PARADO:
            return f"Mascota · pomodoro {self.formato} parado"
        return f"Mascota · {self.fase} {self.reloj()} ({self.formato})"

    def estado(self):
        return {
            "formato": self.formato,
            "fase": self.fase,
            "restante_ms": int(self.restante_ms),
            "restante": self.reloj(),
            "ciclos": self.ciclos,
            "activo": self.activo,
        }

    # -- avisos --------------------------------------------------------------

    def _avisar(self):
        if self._on_cambio:
            self._on_cambio()
