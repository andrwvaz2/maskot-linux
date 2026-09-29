"""Sistema de rutinas: motor simple que ejecuta acciones en secuencia.

Una rutina es una lista de acciones; el motor las va ejecutando una a una
mientras avanza el reloj de la app. No hay hilos ni timers propios: todo avanza
con `tick(dt_ms)`, que llama la ventana principal.

Acciones disponibles (las que se piden):

- `ir_a(x)`      camina hasta la posición horizontal x (None = al azar)
- `decir(t, ms)` muestra un texto en el globo
- `cara(c, ms)`  muestra una expresión (feliz / cansado / pensar)
- `esperar(ms, pose=...)` se queda quieto un rato, con una pose opcional
- `objeto(nombre, x=...)` pone/quita un objeto (banca, libro, taza, portatil)
- `saltar()`      da un salto
- `fin()`         termina la rutina

Rutinas incluidas: `pasear`, `siesta`, `leer_banca`, `echar_codigo` y
`descanso_cafe` (esta última la usa el pomodoro en los descansos).
"""

from __future__ import annotations

import random

import objetos
import sprite as sp

# --- Definición de acciones --------------------------------------------------
# Cada acción es un dict {"tipo": ..., ...params}. Se construyen con las
# funciones de abajo para que las rutinas se lean casi como una lista de pasos.


def ir_a(x=None):
    return {"tipo": "ir_a", "x": x}


def decir(texto, ms=3200):
    return {"tipo": "decir", "texto": texto, "ms": ms}


def cara(nombre, ms=2000):
    return {"tipo": "cara", "nombre": nombre, "ms": ms}


def esperar(ms, pose=None):
    return {"tipo": "esperar", "ms": ms, "pose": pose}


def objeto(nombre, x=None):
    return {"tipo": "objeto", "nombre": nombre, "x": x}


def saltar():
    return {"tipo": "saltar"}


def fin():
    return {"tipo": "fin"}


# --- Rutinas -----------------------------------------------------------------
# `peso` = probabilidad relativa; las tranquilas pesan más. `solo_fases` limita
# la rutina a ciertas fases del pomodoro ("trabajo" / "descanso" / None = todas).

RUTINAS = {
    "pasear": {
        "peso": 2,
        "titulo": "Pasear",
        "pasos": lambda rng: [
            ir_a(rng.randrange(40, 900)),
            esperar(900),
            decir(rng.choice(["de paseo", "qué día más", "hacia el fondo"]),
                  2600),
            cara("feliz", 1800),
            saltar(),
            esperar(600),
        ],
    },
    "siesta": {
        "peso": 3,
        "titulo": "Siesta",
        "pasos": lambda rng: [
            ir_a(rng.randrange(40, 900)),
            esperar(400),
            decir("una siesta corta…", 2400),
            esperar(16000, pose="siesta"),
            cara("feliz", 1500),
        ],
    },
    "leer_banca": {
        "peso": 2,
        "titulo": "Leer en la banca",
        "pasos": lambda rng: [
            ir_a(rng.randrange(60, 700)),
            objeto("banca"),
            esperar(500),
            objeto("libro"),
            decir("shhh, estoy leyendo", 2600),
            esperar(11000, pose="leer"),
            cara("pensar", 1800),
            objeto(None),
        ],
    },
    "echar_codigo": {
        "peso": 1,
        "titulo": "Echar código",
        "pasos": lambda rng: [
            ir_a(rng.randrange(40, 900)),
            objeto("portatil"),
            esperar(400),
            esperar(13000, pose="codigo"),
            saltar(),
            decir(rng.choice(["compilando…", "un bug más", "refactorizando…"]),
                  2600),
            cara("pensar", 2000),
            objeto(None),
        ],
    },
    "descanso_cafe": {
        "peso": 0,          # solo se elige explícitamente (pomodoro en descanso)
        "titulo": "Tomar café",
        "pasos": lambda rng: [
            decir("café ☕", 3000),
            objeto("taza"),
            esperar(9000),
            cara("feliz", 2000),
            objeto(None),
        ],
    },
}

# Objetos que la mascota "lleva" en la mano: se colocan a su lado para que se
# vean (el sprite se dibuja después y los taparía).
OBJETOS_EN_MANO = ("libro", "taza")

# Poses que puede mantener una acción `esperar`.
POSES = ("siesta", "leer", "codigo")

# Frames de apoyo
FRAME_SIESTA = sp.FRAME_SIESTA
FRAME_SIESTA_Z = sp.FRAME_SIESTA_Z
FRAME_LEER = sp.FRAME_LEER
FRAME_CODIGO = sp.FRAME_CODIGO


class MotorRutinas:
    """Ejecuta rutinas sobre la mascota.

    La mascota (`pet`) debe ofrecer esta interfaz:
        sprite,        # objeto Sprite (x, width, direction)
        globo,         # Globo
        max_x(),       # límite derecho del recorrido
        saltar(),      # dispara el salto
        poner_fps(n),  # cambia la frecuencia de animación
        on_cambio()    # avisa de que cambió el estado (para refrescar el menú)
    """

    MIN_SEGUNDO_ENTRE_RUTINAS = 20000
    MAX_SEGUNDO_ENTRE_RUTINAS = 40000
    FPS_DORMIDO = 5

    def __init__(self, pet, rng=None):
        self.pet = pet
        self.rng = rng or random.Random()
        self.nombre = None
        self.pasos = []
        self.indice = 0
        self.accion = None
        self.accion_ms = 0
        self.pose = None
        self.cara_actual = None
        self.cara_ms = 0
        self.saltar_pendiente = False
        self.en_salto = False
        self.salto_t = 0.0
        self.objetos = {}          # nombre -> (x, y) en píxeles
        self.proxima_ms = self._proximo_intervalo()
        self._proxima_peligro = False

    # -- API pública ---------------------------------------------------------

    @property
    def activo(self):
        return self.nombre is not None

    @property
    def durmiendo(self):
        return self.pose == "siesta"

    def estado(self):
        """Descripción del estado actual (para el menú y la API HTTP)."""
        paso = self.accion.get("tipo") if self.accion else None
        return {
            "rutina": self.nombre,
            "titulo": RUTINAS.get(self.nombre, {}).get("titulo"),
            "paso": paso,
            "indice": self.indice,
            "pasos": len(self.pasos),
            "pose": self.pose,
            "cara": self.cara_actual,
            "objetos": sorted(self.objetos),
            "durmiendo": self.durmiendo,
        }

    def iniciar(self, nombre, fase=None):
        """Arranca la rutina `nombre`. Devuelve False si no existe."""
        if nombre not in RUTINAS:
            return False
        self._limpiar()
        pasos = RUTINAS[nombre]["pasos"](self.rng)
        if not pasos:
            return False
        self.nombre = nombre
        self.pasos = list(pasos)
        self.indice = -1
        self._siguiente_accion()
        print(f"[rutinas] empieza '{nombre}' ({len(self.pasos)} pasos)")
        self._avisar()
        return True

    def cancelar(self, motivo=""):
        if not self.activo:
            return False
        nombre = self.nombre
        self._limpiar()
        if motivo:
            print(f"[rutinas] se cancela '{nombre}' ({motivo})")
        self._avisar()
        return True

    def alternar(self):
        if self.activo:
            self.cancelar("a petición")
        else:
            self.iniciar(self.elegir())

    # -- elección de rutina --------------------------------------------------

    def elegir(self, fase=None):
        """Elige rutina al azar; en pomodoro se guía por la fase."""
        candidatas = []
        for nombre, info in RUTINAS.items():
            peso = info.get("peso", 0)
            if peso <= 0:
                continue
            candidatas.append((nombre, peso))
        if fase == "trabajo":
            candidatas = [(n, p) for n, p in candidatas
                          if n in ("echar_codigo", "leer_banca")]
        elif fase == "descanso":
            candidatas = [("descanso_cafe", 1)] + [
                (n, p) for n, p in candidatas if n in ("pasear", "siesta")
            ]
        if not candidatas:
            return "pasear"
        nombres = [n for n, _ in candidatas]
        pesos = [p for _, p in candidatas]
        return self.rng.choices(nombres, weights=pesos, k=1)[0]

    def _proximo_intervalo(self):
        return self.rng.randint(self.MIN_SEGUNDO_ENTRE_RUTINAS,
                                self.MAX_SEGUNDO_ENTRE_RUTINAS)

    # -- bucle ---------------------------------------------------------------

    def tick(self, dt_ms):
        """Avanza la rutina (y, si no hay ninguna, cuenta para la siguiente)."""
        if not self.activo:
            self.proxima_ms -= dt_ms
            if self.proxima_ms <= 0:
                self.iniciar(self.elegir())
            return

        if self.cara_ms > 0:
            self.cara_ms -= dt_ms
            if self.cara_ms <= 0:
                self.cara_actual = None

        if self.accion is not None:
            self.accion_ms -= dt_ms
            if self.accion_ms <= 0:
                self._siguiente_accion()

    # -- acciones ------------------------------------------------------------

    def _siguiente_accion(self):
        self.accion = None
        self.accion_ms = 0
        while True:
            self.indice += 1
            if self.indice >= len(self.pasos):
                self._terminar()
                return
            accion = self.pasos[self.indice]
            tipo = accion.get("tipo")
            if tipo == "ir_a":
                objetivo = accion.get("x")
                if objetivo is None:
                    objetivo = self.rng.randrange(40, max(60, self.pet.max_x() - 40))
                self._ir_a = float(objetivo)
                self.accion_ms = 20000      # tope: si no llega, se cancela
                self.accion = accion
                return
            if tipo == "decir":
                self.pet.globo.mostrar(accion["texto"], accion.get("ms", 3000))
                self.accion_ms = accion.get("ms", 3000)
                self.accion = accion
                return
            if tipo == "cara":
                nombre = accion.get("nombre", "feliz")
                if self.pet.sprite.tiene_cara(nombre) or nombre in sp.FRAMES_CARA:
                    self.cara_actual = nombre
                    self.cara_ms = accion.get("ms", 2000)
                self.accion_ms = accion.get("ms", 2000)
                self.accion = accion
                return
            if tipo == "esperar":
                pose = accion.get("pose")
                self.pose = pose if pose in POSES else None
                self.pet.poner_fps(self.FPS_DORMIDO if pose == "siesta" else None)
                self.accion_ms = accion.get("ms", 1000)
                self.accion = accion
                return
            if tipo == "objeto":
                nombre = accion.get("nombre")
                if nombre is None:
                    self.objetos.clear()
                else:
                    x = accion.get("x")
                    if x is None:
                        x = self.pet.sprite.x
                        if nombre in OBJETOS_EN_MANO:
                            x += self.pet.sprite.width * 0.8
                    # El objeto se apoya en el suelo, no en su parte de abajo.
                    alto = objetos.TAMANOS.get(nombre, (0, 1))[1] * self.pet.sprite.scale
                    self.objetos[nombre] = (float(x), self.pet.suelo_y() - alto)
                self.accion_ms = 1
                self.accion = accion
                return
            if tipo == "saltar":
                self.saltar_pendiente = True
                self.accion_ms = 1
                self.accion = accion
                return
            if tipo == "fin":
                self._terminar()
                return
            # Acción desconocida: se ignora y se sigue.
            print(f"[rutinas] acción desconocida: {tipo!r}")

    def _terminar(self):
        nombre = self.nombre
        self._limpiar()
        print(f"[rutinas] termina '{nombre}'")
        self._avisar()

    def _limpiar(self):
        self.nombre = None
        self.pasos = []
        self.indice = 0
        self.accion = None
        self.accion_ms = 0
        self.pose = None
        self.cara_actual = None
        self.cara_ms = 0
        self.saltar_pendiente = False
        self.objetos.clear()
        self._ir_a = None
        self.proxima_ms = self._proximo_intervalo()
        self.pet.poner_fps(None)
        self._avisar()

    def _avisar(self):
        avisar = getattr(self.pet, "on_cambio", None)
        if avisar:
            avisar()

    # -- dibujo / movimiento -------------------------------------------------

    def mover(self, dt_ms):
        """Mueve el sprite si la rutina actual es `ir_a`."""
        if self.accion is None or self.accion.get("tipo") != "ir_a":
            return False
        objetivo = getattr(self, "_ir_a", None)
        if objetivo is None:
            return False
        sprite = self.pet.sprite
        max_x = self.pet.max_x()
        objetivo = max(0.0, min(float(objetivo), float(max_x)))
        paso = 4.0 * (dt_ms / 50.0)      # 4 px por tick de 50 ms
        if abs(sprite.x - objetivo) <= paso:
            sprite.x = objetivo
            return True
        direccion = 1 if objetivo > sprite.x else -1
        sprite.x = max(0.0, min(sprite.x + paso * direccion, float(max_x)))
        sprite.direction = direccion
        return False

    def frame_actual(self, walk_frame):
        """Devuelve el frame que toca dibujar ahora mismo."""
        sp = self.pet.sprite
        if self.cara_actual:
            return sp.frame_cara(self.cara_actual)
        if self.pose == "siesta":
            return sp.frame_siesta_z if self._medio_tick() else sp.frame_siesta
        if self.pose == "leer":
            return sp.frame_leer
        if self.pose == "codigo":
            return sp.frame_codigo
        if self.en_salto:
            return sp.frame_jump
        return walk_frame

    def _medio_tick(self):
        """Alterna True/False para las 'Zzz' sin depender del reloj."""
        self._z = not getattr(self, "_z", False)
        return self._z
