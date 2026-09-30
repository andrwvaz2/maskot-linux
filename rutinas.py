"""Sistema de rutinas: motor simple que ejecuta acciones en secuencia.

Una rutina es una lista de acciones; el motor las va ejecutando una a una
mientras avanza el reloj de la app. No hay hilos ni timers propios: todo avanza
con `tick(dt_ms)`, que llama la ventana principal.

Acciones disponibles (las que se piden):

- `ir_a(x, al_llegar=...)` camina hasta la posición horizontal x (None = al azar)
- `decir(t, ms)` muestra un texto en el globo
- `cara(c, ms)`  muestra una expresión (feliz / cansado / pensar)
- `esperar(ms, pose=..., texto=...)` se queda quieto un rato, con pose y texto
- `objeto(nombre, x=..., y=...)` pone/mueve un objeto (banca, libro, taza,
  portátil, papelera, hoja, regadera, plantita)
- `quitar(nombre)` retira un solo objeto y deja los demás en su sitio
- `cuenta_atras(n, ms)` cuenta 3-2-1 en el globo (la misma que la pausa activa)
- `saltar()`      da un salto
- `fin()`         termina la rutina

Rutinas incluidas: `pasear`, `siesta`, `leer_banca`, `echar_codigo`,
`descanso_cafe` (esta última la usa el pomodoro en los descansos),
`hoja_a_caneca`, `matica` y `respiracion`.
"""

from __future__ import annotations

import inspect
import random

import objetos
import sprite as sp
from pausa import CuentaAtras

# --- Definición de acciones --------------------------------------------------
# Cada acción es un dict {"tipo": ..., ...params}. Se construyen con las
# funciones de abajo para que las rutinas se lean casi como una lista de pasos.


def ir_a(x=None, ms=None, al_llegar=False):
    """Camina hasta `x` (None = al azar).

    Sin `ms`, el paso dura lo que el tope por defecto (20 s) aunque el sprite
    llegue antes. Con `al_llegar=True` la rutina sigue en cuanto llega, que es
    lo que necesitan las rutinas cortas.
    """
    return {"tipo": "ir_a", "x": x, "ms": ms, "al_llegar": al_llegar}


def decir(texto, ms=3200):
    return {"tipo": "decir", "texto": texto, "ms": ms}


def cara(nombre, ms=2000):
    return {"tipo": "cara", "nombre": nombre, "ms": ms}


def esperar(ms, pose=None, texto=None):
    return {"tipo": "esperar", "ms": ms, "pose": pose, "texto": texto}


def objeto(nombre, x=None, y=None):
    return {"tipo": "objeto", "nombre": nombre, "x": x, "y": y}


def quitar(nombre):
    """Retira un objeto del escenario sin tocar el resto."""
    return {"tipo": "quitar", "nombre": nombre}


def cuenta_atras(n=3, ms=1000, texto="Respira en {n}…", duracion=900):
    return {"tipo": "cuenta_atras", "n": n, "ms": ms, "texto": texto,
            "duracion": duracion}


def saltar():
    return {"tipo": "saltar"}


def fin():
    return {"tipo": "fin"}


# --- Rutinas -----------------------------------------------------------------
# `peso` = probabilidad relativa; las tranquilas pesan más. `solo_fases` limita
# la rutina a ciertas fases del pomodoro ("trabajo" / "descanso" / None = todas).

# Días de uso a partir de los cuales la plantita cambia de etapa.
UMBRAL_BROTE = 3
UMBRAL_FLOR = 15

# Las tres etapas de la plantita, en orden de crecimiento (ver objetos.py).
ETAPAS_PLANTA = ("planta_semilla", "planta_brote", "planta_flor")


def etapa_planta(dias):
    """Etapa de la plantita según los días de uso: 0 semilla, 1 brote, 2 flor."""
    if dias >= UMBRAL_FLOR:
        return 2
    if dias >= UMBRAL_BROTE:
        return 1
    return 0


def _dias_de_uso(pet):
    """Días de uso de las preferencias (0 si la mascota no las expone)."""
    prefs = getattr(pet, "prefs", None)
    try:
        return max(0, int(prefs.dias_uso)) if prefs is not None else 0
    except (AttributeError, TypeError, ValueError):
        return 0


def _ancho_recorrido(pet):
    """Límite derecho del recorrido (el borde de la barra, ya a todo lo ancho).

    Antes del primer dibujo la ventana todavía no tiene anchura (`max_x()` da
    0); en ese caso se usa un valor de reserva para no quedarnos sin sitio.
    """
    max_x = int(getattr(pet, "max_x", lambda: 0)() or 0)
    return max_x if max_x > 0 else 930


def _a_la_derecha(rng, pet, minimo, maximo):
    """Posición a `minimo..maximo` px a la derecha de la mascota.

    Se parte de su posición real para que estas rutinas cortas no empiecen con
    un paseo de ida y vuelta por toda la barra, y se ajusta al borde para que
    un objeto nunca aparezca a medio cortar (solo pasa cerca del final del
    recorrido).
    """
    tope = _ancho_recorrido(pet)
    origen = max(0.0, float(getattr(pet.sprite, "x", 0.0) or 0.0))
    return int(max(0.0, min(tope, origen + rng.randrange(minimo, maximo))))


def _pasos_hoja_a_caneca(rng, pet):
    """Recoge una hoja del suelo y la tira a una papelera cercana."""
    papelera_x = _a_la_derecha(rng, pet, 220, 340)
    # La mascota se para a la izquierda de la papelera (si se pone encima, el
    # sprite la tapa y no se ve ni el bote ni la hoja que cae dentro).
    tirar_x = max(0.0, papelera_x - 120)
    hoja_x = max(0.0, tirar_x - 100)
    # Altura a la que la hoja "cabe dentro" de la papelera.
    dentro = (pet.suelo_y()
              - objetos.TAMANOS["papelera"][1] * pet.sprite.scale * 0.6)
    return [
        objeto("papelera", x=papelera_x),
        ir_a(hoja_x, al_llegar=True),
        objeto("hoja", x=max(0, hoja_x + rng.randrange(-20, 20))),
        esperar(500),
        decir(rng.choice(["¿qué hace esta hoja aquí?",
                          "esta hoja no estaba antes",
                          "papel tirado"]), 2600),
        esperar(300),
        objeto("hoja"),                    # la recoge: pasa a la mano
        esperar(700),
        decir("a la papelera", 1800),
        ir_a(tirar_x, al_llegar=True),
        esperar(300),
        objeto("hoja", x=papelera_x, y=dentro),   # la hoja cae dentro
        esperar(800),
        quitar("hoja"),
        saltar(),
        decir(rng.choice(["listo", "fuera", "bien"]), 1800),
        cara("feliz", 1600),
    ]


def _pasos_matica(rng, pet):
    """Riega la plantita; crece según los días de uso de las preferencias."""
    dias = _dias_de_uso(pet)
    etapa = etapa_planta(dias)
    planta_x = _a_la_derecha(rng, pet, 90, 200)
    pasos = [
        objeto(ETAPAS_PLANTA[etapa], x=planta_x),
        ir_a(max(0.0, planta_x - 70), al_llegar=True),
        esperar(400),
        decir(rng.choice(["hora de regar", "sed thirsty",
                          "voy a regarla"]), 2200),
        esperar(300),
        objeto("regadera"),
        esperar(400),
        esperar(3200, pose="regar", texto="regando…"),
        quitar("regadera"),
        esperar(300),
        cara("feliz", 1400),
    ]
    if etapa < 2:
        # Al regarla da un estirón: se sustituye por la etapa siguiente, en
        # el mismo sitio (si no, la planta vieja se quedaría en pantalla).
        pasos += [
            quitar(ETAPAS_PLANTA[etapa]),
            objeto(ETAPAS_PLANTA[etapa + 1], x=planta_x),
            decir(rng.choice(["¡y ha crecido!", "¡qué rápido!"]), 2200),
        ]
    else:
        pasos += [decir(f"día {dias} cuidándola", 2400)]
    return pasos


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
    "hoja_a_caneca": {
        "peso": 1,
        "titulo": "Echar la hoja",
        "pasos": _pasos_hoja_a_caneca,
    },
    "matica": {
        "peso": 1,
        "titulo": "Regar la plantita",
        "pasos": _pasos_matica,
    },
    "respiracion": {
        "peso": 1,
        "titulo": "Respirar",
        "pasos": lambda rng: [
            decir("respiramos un momento", 2400),
            esperar(400),
            cuenta_atras(3, 1000, "Respira en {n}…"),
            esperar(4000, pose="respirar", texto="Inhala…"),
            esperar(4000, texto="Exhala…"),
            esperar(4000, pose="respirar", texto="Inhala…"),
            esperar(4000, texto="Exhala…"),
            cara("feliz", 1800),
            decir("qué bien", 2000),
        ],
    },
}

# Objetos que la mascota "lleva" en la mano: se colocan a su lado para que se
# vean (el sprite se dibuja después y los taparía).
OBJETOS_EN_MANO = ("libro", "taza", "regadera", "hoja")

# Poses que puede mantener una acción `esperar`. `regar` y `respirar` no tienen
# cuadro propio todavía y reutilizan los que ya hay: mirar hacia abajo (el de
# la laptop) y brazos en alto (el del estiramiento).
POSES = ("siesta", "leer", "codigo", "regar", "respirar")

# Frames de apoyo
FRAME_SIESTA = sp.FRAME_SIESTA
FRAME_SIESTA_Z = sp.FRAME_SIESTA_Z
FRAME_LEER = sp.FRAME_LEER
FRAME_CODIGO = sp.FRAME_CODIGO


def _llamar_pasos(fn, rng, pet):
    """Llama a `fn(rng)` o a `fn(rng, pet)`, según lo que acepte.

    Las rutinas antiguas solo necesitan el azar; las que leen el estado de la
    mascota (por ejemplo `matica` con los días de uso) piden el segundo
    argumento, así que no hay que tocar las definiciones antiguas.
    """
    try:
        acepta_pet = len(inspect.signature(fn).parameters) >= 2
    except (TypeError, ValueError):
        acepta_pet = False
    return fn(rng, pet) if acepta_pet else fn(rng)


class MotorRutinas:
    """Ejecuta rutinas sobre la mascota.

    La mascota (`pet`) debe ofrecer esta interfaz:
        sprite,        # objeto Sprite (x, width, direction, scale)
        globo,         # Globo
        max_x(),       # límite derecho del recorrido
        suelo_y(),     # altura del suelo (para apoyar objetos)
        prefs,         # preferencias (opcional: días de uso de `matica`)
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
        self._cuenta = None        # CuentaAtras si la acción actual es una cuenta
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
            "cuenta_atras": self._cuenta.valor if self._cuenta else 0,
            "durmiendo": self.durmiendo,
        }

    def iniciar(self, nombre, fase=None):
        """Arranca la rutina `nombre`. Devuelve False si no existe."""
        if nombre not in RUTINAS:
            return False
        self._limpiar()
        pasos = _llamar_pasos(RUTINAS[nombre]["pasos"], self.rng, self.pet)
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
            if self.accion.get("tipo") == "cuenta_atras" and self._cuenta:
                self._cuenta.tick(dt_ms)
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
                self.accion_ms = accion.get("ms") or 20000   # tope: si no llega
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
                texto = accion.get("texto")
                if texto:
                    self.pet.globo.mostrar(texto, accion.get("ms", 1000))
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
                    y = accion.get("y")
                    if y is None:
                        # El objeto se apoya en el suelo, no en su parte de abajo.
                        alto = objetos.TAMANOS.get(nombre, (0, 1))[1] * self.pet.sprite.scale
                        y = self.pet.suelo_y() - alto
                    self.objetos[nombre] = (float(x), float(y))
                self.accion_ms = 1
                self.accion = accion
                return
            if tipo == "quitar":
                self.objetos.pop(accion.get("nombre"), None)
                self.accion_ms = 1
                self.accion = accion
                return
            if tipo == "cuenta_atras":
                # La misma cuenta 3-2-1 de la pausa activa (pausa.CuentaAtras).
                self._cuenta = CuentaAtras(
                    self.pet,
                    desde=accion.get("n", 3),
                    ms_por_numero=accion.get("ms", 1000),
                    plantilla=accion.get("texto") or "… {n} …",
                    duracion_globo=accion.get("duracion", 900),
                )
                self._cuenta.iniciar()
                self.accion_ms = max(1, self._cuenta.desde
                                     * self._cuenta.ms_por_numero)
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
        self._cuenta = None
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
        antes = sprite.x
        if abs(sprite.x - objetivo) <= paso:
            sprite.x = objetivo
            self._acompañar_mano(sprite.x - antes)
            if self.accion.get("al_llegar"):
                self.accion_ms = 0      # la rutina sigue al llegar
            return True
        direccion = 1 if objetivo > sprite.x else -1
        sprite.x = max(0.0, min(sprite.x + paso * direccion, float(max_x)))
        sprite.direction = direccion
        self._acompañar_mano(sprite.x - antes)
        return False

    def _acompañar_mano(self, desplazamiento):
        """Mueve con el sprite lo que lleva en la mano (libro, hoja, taza…)."""
        if not desplazamiento or not self.objetos:
            return
        for nombre in OBJETOS_EN_MANO:
            if nombre in self.objetos:
                x, y = self.objetos[nombre]
                self.objetos[nombre] = (x + desplazamiento, y)

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
        if self.pose == "regar":
            return sp.frame_codigo       # mirando hacia abajo
        if self.pose == "respirar":
            return sp.frame_estirar      # brazos en alto
        if self.en_salto:
            return sp.frame_jump
        return walk_frame

    def _medio_tick(self):
        """Alterna True/False para las 'Zzz' sin depender del reloj."""
        self._z = not getattr(self, "_z", False)
        return self._z
