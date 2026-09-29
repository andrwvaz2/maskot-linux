"""Catálogo de Personajes para Maskot (Linux).

Incluye:
- Tux (el pingüino de Linux — diseño nativo para esta edición)
- La familia Koru (adaptados de alecap92/maskot-mac bajo licencia MIT):
    * Koru (el cangrejito curioso)
    * Clawd (el cangrejito con gorra)
    * Tuno (el zorro ingenioso)
    * Nilo (la tortuga confiable)
    * Brio (la abeja veloz)
    * Luma (el búho observador)
    * Mako (el gecko ágil)
    * Orbi (el pulpo versátil)

Cada personaje provee su paleta de colores Cairo (0..1) y sus cuadros de
animación en grilla de 16x16:
- walk_a, walk_b (caminata cíclica)
- jump (salto / patas recogidas)
- siesta (ojos cerrados)
- siesta_z (siesta con "Zzz" flotando)
- leer (mirada baja al libro)
- codigo (concentrado frente a la laptop)
- estirar (brazos en alto / estiramiento)
- caras: feliz, cansado, pensar
"""

from __future__ import annotations


def hex_to_rgb(h):
    if isinstance(h, str):
        h = int(h.replace("#", "").replace("0x", ""), 16)
    return (round(((h >> 16) & 0xFF) / 255.0, 3),
            round(((h >> 8) & 0xFF) / 255.0, 3),
            round((h & 0xFF) / 255.0, 3))


# Paleta base general
PALETA_BASE_TINTAS = {
    "c": (0.851, 0.467, 0.341),  # cuerpo base terracota
    "o": (0.078, 0.078, 0.078),  # ojo
    "r": (0.949, 0.557, 0.608),  # cachete / rubor
    "g": (0.169, 0.298, 0.494),  # gorra
    "v": (0.110, 0.204, 0.337),  # visera
    "b": (0.357, 0.498, 0.710),  # correa
    "s": (0.949, 0.627, 0.710),  # chispa rosa
    "n": (0.957, 0.635, 0.380),  # chispa naranja
    "z": (0.541, 0.580, 0.651),  # zeta
    "p": (0.541, 0.580, 0.651),  # punto
    "w": (0.969, 0.961, 0.933),  # papel
    "l": (0.725, 0.765, 0.827),  # renglón
    "k": (0.490, 0.525, 0.588),  # borde
    "O": (0.086, 0.227, 0.388),  # contorno azul marino (#163A63)
    "C": (0.969, 0.949, 0.910),  # crema
    "1": (0.467, 0.737, 0.910),  # detalle 1
    "2": (0.812, 0.910, 0.969),  # detalle 2
    "3": (0.961, 0.827, 0.220),  # detalle 3
    "4": (0.663, 0.541, 0.910),  # detalle 4
    "5": (1.000, 1.000, 1.000),  # brillo blanco
    "Z": (0.750, 0.800, 0.950),  # Zzz siesta
    "K": (0.130, 0.120, 0.160),  # contorno genérico
    "B": (0.040, 0.040, 0.070),  # ojos oscuros
    "P": (0.960, 0.520, 0.580),  # rubor
}


def aplicar_cuadro(cuerpo, overlays=None, clears=None):
    """Genera un cuadro de 16x16 aplicando reemplazos y borrados sobre el cuerpo base."""
    cuadro = [list(fila) for fila in cuerpo]
    if clears:
        for r, cols in clears:
            if 0 <= r < 16:
                for c in cols:
                    if 0 <= c < 16:
                        cuadro[r][c] = "."
    if overlays:
        for r, linea in overlays.items():
            if 0 <= r < 16:
                for c, ch in enumerate(linea):
                    if ch != "." and 0 <= c < 16:
                        cuadro[r][c] = ch
    return tuple("".join(fila) for fila in cuadro)


class Personaje:
    def __init__(self, id, nombre, desc, paleta_override, cuerpo,
                 cara_neutro, caras, patas_fila, paso1, paso2,
                 brazos_arriba=None, brazos_tecleo=None, cara_dormido=None,
                 cara_leer=None, cara_codigo=None, extras=None):
        self.id = id
        self.nombre = nombre
        self.desc = desc
        self.cuerpo = cuerpo

        # Combinar paleta base con las tintas propias del personaje
        self.paleta = dict(PALETA_BASE_TINTAS)
        self.paleta.update(paleta_override)

        # Caras base
        cara_dorm = cara_dormido or {7: "....oo....oo....", 9: ".......OO......."}
        cara_le = cara_leer or {7: ".....5o..5o.....", 8: ".....oo..oo....."}
        cara_cod = cara_codigo or caras.get("pensar") or cara_neutro

        # 1. Caminata (alternando levantamiento de patas)
        f_walk_a = aplicar_cuadro(cuerpo, overlays=cara_neutro, clears=[(patas_fila, paso1)])
        f_walk_b = aplicar_cuadro(cuerpo, overlays=cara_neutro, clears=[(patas_fila, paso2)])

        # 2. Salto (todas las patas recogidas)
        f_jump = aplicar_cuadro(cuerpo, overlays=caras.get("feliz", cara_neutro),
                               clears=[(patas_fila, paso1 + paso2)])

        # 3. Siesta
        f_siesta = aplicar_cuadro(cuerpo, overlays=cara_dorm)
        z_overlay = dict(cara_dorm)
        z_overlay[0] = "............ZZ.."
        z_overlay[1] = "..........ZZ...."
        f_siesta_z = aplicar_cuadro(cuerpo, overlays=z_overlay)

        # 4. Leer
        f_leer = aplicar_cuadro(cuerpo, overlays=cara_le)

        # 5. Código (laptop)
        cod_overlay = dict(cara_cod)
        if brazos_tecleo:
            cod_overlay.update(brazos_tecleo)
        f_codigo = aplicar_cuadro(cuerpo, overlays=cod_overlay)

        # 6. Estirar (pausa activa / brazos en alto)
        estirar_overlay = dict(caras.get("feliz", cara_neutro))
        if brazos_arriba:
            estirar_overlay.update(brazos_arriba)
        f_estirar = aplicar_cuadro(cuerpo, overlays=estirar_overlay)

        self.frames = {
            "walk_a": f_walk_a,
            "walk_b": f_walk_b,
            "jump": f_jump,
            "siesta": f_siesta,
            "siesta_z": f_siesta_z,
            "leer": f_leer,
            "codigo": f_codigo,
            "estirar": f_estirar,
        }

        # Caras para la acción cara(...)
        self.caras = {
            "feliz": aplicar_cuadro(cuerpo, overlays=caras.get("feliz", cara_neutro)),
            "cansado": aplicar_cuadro(cuerpo, overlays=caras.get("cansado", cara_dorm)),
            "pensar": aplicar_cuadro(cuerpo, overlays=caras.get("pensar", cara_neutro)),
        }

# ---------------------------------------------------------------------------
# 1. TUX — El pingüino de Linux
# ---------------------------------------------------------------------------
CUERPO_TUX = (
    "................",
    ".....OOOOOO.....",
    "....OccccccO....",
    "...Occ5o5occO...",
    "...Oc111111cO...",
    "..OOcCCCCCCccOO.",
    ".OccCCCCCCCCccO.",
    ".OccCCCCCCCCccO.",
    "OccCCCCCCCCCCCCO",
    "OccCCCCCCCCCCCCO",
    "OccCCCCCCCCCCCCO",
    ".OccCCCCCCCCccO.",
    "..OOccccccccccO.",
    "...OOOOOOOOOO...",
    "...O111O..O111O.",
    "...O222O..O222O.",
)

PALETA_TUX = {
    "O": hex_to_rgb(0x111827),  # contorno oscuro
    "c": hex_to_rgb(0x1F2937),  # cuerpo carbón
    "C": (0.98, 0.98, 0.98),    # blanco vientre
    "1": hex_to_rgb(0xF59E0B),  # pico y patas
    "2": hex_to_rgb(0xD97706),  # sombra pico y patas
    "o": hex_to_rgb(0x111827),  # ojos
    "5": (1.0, 1.0, 1.0),       # brillo
    "r": hex_to_rgb(0xF58594),  # rubor
}

TUX = Personaje(
    id="tux",
    nombre="Tux",
    desc="El legendario pingüino de Linux",
    paleta_override=PALETA_TUX,
    cuerpo=CUERPO_TUX,
    cara_neutro={3: "...Occ5o5occO...", 4: "...Oc111111cO..."},
    caras={
        "feliz": {3: "...Occ5o5occO...", 4: "...Oc111111cO...", 5: "..OOcCr11rCccOO."},
        "cansado": {3: "...Occoo..ooccO...", 4: "...Oc111111cO..."},
        "pensar": {3: "...Occ5o..o5ccO...", 4: "...Oc111111cO..."},
    },
    patas_fila=15,
    paso1=[3, 4, 5, 6],
    paso2=[10, 11, 12, 13],
    brazos_arriba={2: "..Oc........cO..", 3: ".Occ........ccO.", 6: "..OOcCCCCCCccOO."},
    brazos_tecleo={6: "..OOc11CCCC11cOO", 7: ".Occ11CCCC11ccO."},
    cara_dormido={3: "...Occoo..ooccO...", 4: "...Oc111111cO..."},
    cara_leer={3: "...Occ....ccO...", 4: "...Occ5o5occO...", 5: "..OOcCCCCCCccOO."},
    cara_codigo={3: "...Occ5o5occO...", 4: "...Oc111111cO..."},
)

# ---------------------------------------------------------------------------
# 2. KORU — El cangrejito curioso
# ---------------------------------------------------------------------------
CUERPO_KORU = (
    "................",
    "................",
    "................",
    ".OO.OOOOOOOO.OO.",
    "O1cO33ccccccOc1O",
    "OOcO3cccccccOcOO",
    "..OOccccccccOO..",
    "OOccccccccccccOO",
    "O1cccccccccccc1O",
    "OccccccccccccccO",
    ".OOccccccccccOO.",
    "..OccccccccccO..",
    "..O2222222222O..",
    "...OOOOOOOOOO...",
    "...O.O....O.O...",
    "..O..O....O..O..",
)

PALETA_KORU = {
    "c": hex_to_rgb(0xF26A2E),  # terracota
    "1": hex_to_rgb(0x77BCE8),  # azul claro: puntas de las pinzas
    "2": hex_to_rgb(0xD2521C),  # terracota sombra
    "3": hex_to_rgb(0xFF9C66),  # terracota con luz
}

KORU = Personaje(
    id="koru",
    nombre="Koru",
    desc="Cangrejo curioso, explorador del sistema",
    paleta_override=PALETA_KORU,
    cuerpo=CUERPO_KORU,
    cara_neutro={6: ".....5o..5o.....", 7: ".....oo..oo.....", 9: ".......OO......."},
    caras={
        "feliz": {6: ".....o....o.....", 7: "....o.o..o.o....", 9: "......OOOO......"},
        "cansado": {7: "....ooo..ooo....", 9: ".......OO......."},
        "pensar": {5: "......5o..5o....", 6: "......oo..oo....", 9: "........OO......"},
    },
    patas_fila=15,
    paso1=[2, 10],
    paso2=[5, 13],
    brazos_arriba={3: ".OO.OO....OO.OO.", 4: "O1cO33....33Oc1O", 2: "O1c..........c1O"},
    brazos_tecleo={8: "O1cccccccccccc1O", 9: "OccccccccccccccO"},
    cara_dormido={7: "....ooo..ooo....", 9: ".......OO......."},
    cara_leer={7: ".....5o..5o.....", 8: ".....oo..oo.....", 9: "................"},
    cara_codigo={5: "....oooooooo....", 6: "....o55oo55o....", 7: "....o5ooo5oo....", 8: "....oooooooo...."},
)

# ---------------------------------------------------------------------------
# 3. CLAWD — El cangrejito con gorra deportiva
# ---------------------------------------------------------------------------
CUERPO_CLAWD = (
    "................",
    "................",
    "......vvvv......",
    ".....gggggg.....",
    "....gggbbggg....",
    "...gggbccbggg...",
    "..cccccccccccc..",
    "..cccccccccccc..",
    "..cccccccccccc..",
    "..cccccccccccc..",
    "..cccccccccccc..",
    "cccccccccccccccc",
    "cccccccccccccccc",
    "..cccccccccccc..",
    "...c.c....c.c...",
    "...c.c....c.c...",
)

PALETA_CLAWD = {
    "c": hex_to_rgb(0xD97757),  # terracota
    "g": hex_to_rgb(0x2B4C7E),  # gorra
    "v": hex_to_rgb(0x1C3456),  # visera
    "b": hex_to_rgb(0x5B7FB5),  # correa
}

CLAWD = Personaje(
    id="clawd",
    nombre="Clawd",
    desc="Cangrejo con gorra deportiva hacia atrás",
    paleta_override=PALETA_CLAWD,
    cuerpo=CUERPO_CLAWD,
    cara_neutro={9: "....o......o....", 10: "....o......o...."},
    caras={
        "feliz": {8: "....o......o....", 9: ".....o....o.....", 10: "....o......o...."},
        "cansado": {10: "....oo....oo...."},
        "pensar": {8: ".....o......o...", 9: ".....o......o..."},
    },
    patas_fila=15,
    paso1=[3, 10],
    paso2=[5, 12],
    brazos_arriba={6: ".c............c.", 7: "cc............cc"},
    brazos_tecleo={11: "cccccccccccccccc", 12: "..cccccccccccc.."},
    cara_dormido={10: "....oo....oo...."},
    cara_leer={10: ".....o....o....."},
    cara_codigo={8: "...oooo..oooo...", 9: "...owwoooowwo...", 10: "...owoo..owoo...", 11: "...oooo..oooo..."},
)

# ---------------------------------------------------------------------------
# 4. TUNO — El zorro ingenioso
# ---------------------------------------------------------------------------
CUERPO_TUNO = (
    "...O..........O.",
    "...OO........OO.",
    "...O1O......O1O.",
    "...O11O....O11O.",
    "...Oc11OOOO11cO.",
    "...OccccccccccO.",
    ".OOOccccccccccO.",
    "OCCOccccccccccO.",
    "OCcOCCccccccCCCO",
    "OccOCCCCCCCCCCO.",
    "Occ2OcCCCCCCcO..",
    "Occ2OcCCCCCCcO..",
    "Oc22OccCCCCccO..",
    "Oc22OccccccccO..",
    ".O22OccOOOOccO..",
    "..OOOccO..OccO..",
)

PALETA_TUNO = {
    "c": hex_to_rgb(0xF58A2A),  # naranja zorro
    "1": hex_to_rgb(0x53C3D8),  # cian orejas
    "2": hex_to_rgb(0xC76510),  # sombra cola
    "C": hex_to_rgb(0xFFF2DD),  # crema vientre/pecho
}

TUNO = Personaje(
    id="tuno",
    nombre="Tuno",
    desc="Zorro ingenioso y estratega",
    paleta_override=PALETA_TUNO,
    cuerpo=CUERPO_TUNO,
    cara_neutro={6: "...Oc5occc5occO.", 7: "...OcoocccooccO.", 8: "...OCCccccOcCCCO", 9: "...OCCCCOOCCCCO."},
    caras={
        "feliz": {6: "...OcoocccooccO.", 7: "...OoccococcocO.", 8: "...OCCCCOOCCCCO."},
        "cansado": {6: "...OccccccccccO.", 7: "...OcoocccooccO.", 8: "...OCCCCOOCCCCO."},
        "pensar": {6: "...Oc5occcccccO.", 7: "...OcoocccccccO.", 8: "...OCCCCOOCCCCO."},
    },
    patas_fila=15,
    paso1=[5, 6],
    paso2=[11, 12],
    brazos_arriba={5: "..Oc..........cO"},
    brazos_tecleo={9: "OccOCCCCCCCCCC1O"},
    cara_dormido={6: "...OccccccccccO.", 7: "...OcoocccooccO."},
    cara_leer={7: "...Oc5occc5occO.", 8: "...OcoocccooccO."},
    cara_codigo={6: "...Oc5occc5occO.", 7: "...OcoocccooccO."},
)

# ---------------------------------------------------------------------------
# 5. NILO — La tortuga confiable
# ---------------------------------------------------------------------------
CUERPO_NILO = (
    "................",
    "................",
    "....OOOO........",
    "...O2222O.......",
    "..O221111O......",
    ".O21311OOOOOO...",
    "O21311OccccccO..",
    "O3331OccccccccO.",
    "O1131OccccccccO.",
    "O1131OccccccccO.",
    "O3333OccccccccO.",
    "O1131OccccccccO.",
    "O33333OccccccO..",
    ".OccOCCCCCCOccO.",
    ".OccOOOOOOOOccO.",
    ".OOOO......OOOO.",
)

PALETA_NILO = {
    "c": hex_to_rgb(0xA8DB55),  # verde tortuga
    "1": hex_to_rgb(0x249CB8),  # teal caparazón
    "2": hex_to_rgb(0x1A7085),  # sombra caparazón
    "3": hex_to_rgb(0x53C3D8),  # brillo caparazón
    "C": hex_to_rgb(0xF6ECD7),  # crema plastrón
}

NILO = Personaje(
    id="nilo",
    nombre="Nilo",
    desc="Tortuga paciente y confiable",
    paleta_override=PALETA_NILO,
    cuerpo=CUERPO_NILO,
    cara_neutro={7: "O3331Oc5occ5ocO.", 8: "O1131OcooccoocO.", 9: "O1131OccOccOccO."},
    caras={
        "feliz": {7: "O3331OcoccccocO.", 8: "O1131OococcocoO.", 9: "O1131OccOccOccO."},
        "cansado": {7: "O3331OccccccccO.", 8: "O1131OcooccoocO.", 9: "O1131OccOccOccO."},
        "pensar": {7: "O3331Occcc5occO.", 8: "O1131OcccccoocO.", 9: "O1131OccOccOccO."},
    },
    patas_fila=15,
    paso1=[1, 2, 3, 4],
    paso2=[11, 12, 13, 14],
    brazos_arriba={6: "O21311Occ..ccO..", 7: "O3331OccccccccO."},
    brazos_tecleo={9: "O1131OccccccccO.", 10: "O3333OccccccccO."},
    cara_dormido={7: "O3331OccccccccO.", 8: "O1131OcooccoocO."},
    cara_leer={8: "O1131Oc5occ5ocO.", 9: "O1131OcooccoocO."},
    cara_codigo={7: "O3331Oc5occ5ocO.", 8: "O1131OcooccoocO."},
)

# ---------------------------------------------------------------------------
# 6. BRIO — La abeja veloz
# ---------------------------------------------------------------------------
CUERPO_BRIO = (
    "OOO..c....c..OOO",
    "O11O..O..O..O11O",
    "O151O.O..O.O151O",
    ".O111OOOOOO111O.",
    "..O1OccccccO1O..",
    "..OOccccccccOO..",
    "..OccccccccccO..",
    ".OccccccccccccO.",
    ".OccccccccccccO.",
    ".OccccccccccccO.",
    "OOccccccccccccOO",
    "OcOOOOOOOOOOOOcO",
    "OcOccccccccccOcO",
    ".O.OOOOOOOOOO.O.",
    "......O..O......",
    ".....OO..OO.....",
)

PALETA_BRIO = {
    "c": hex_to_rgb(0xF5D338),  # amarillo abeja
    "1": hex_to_rgb(0xA7DDF8),  # alas celeste
    "5": (1.0, 1.0, 1.0),       # brillo blanco
}

BRIO = Personaje(
    id="brio",
    nombre="Brio",
    desc="Abeja veloz y eficiente",
    paleta_override=PALETA_BRIO,
    cuerpo=CUERPO_BRIO,
    cara_neutro={6: "..O.5o....5o.O..", 7: ".O..oo....oo..O.", 8: ".O....O..O....O.", 9: ".O....OOOO....O."},
    caras={
        "feliz": {6: "..O.oo....oo.O..", 7: ".O.o..o..o..o.O.", 8: ".O....OOOO....O."},
        "cansado": {7: ".O..oo....oo..O.", 8: ".O....O..O....O."},
        "pensar": {6: "..O...5o....5oO.", 7: ".O....oo....ooO."},
    },
    patas_fila=15,
    paso1=[5, 6],
    paso2=[9, 10],
    brazos_arriba={4: ".O1OccccccO1O...", 5: "O.OOccccccccOO.O"},
    brazos_tecleo={9: ".OccccccccccccO."},
    cara_dormido={7: ".O..oo....oo..O.", 8: ".O....O..O....O."},
    cara_leer={7: ".O..5o....5o..O.", 8: ".O..oo....oo..O."},
    cara_codigo={6: "..O.5o....5o.O..", 7: ".O..oo....oo..O."},
)

# ---------------------------------------------------------------------------
# 7. LUMA — El búho observador
# ---------------------------------------------------------------------------
CUERPO_LUMA = (
    ".OO..........OO.",
    ".OcO........OcO.",
    ".OccOOOOOOOOccO.",
    ".Occcc1111ccccO.",
    ".OcccCCccCCcccO.",
    ".OccCCCCCCCCccO.",
    ".OccCCCCCCCCccO.",
    ".OccCCCCCCCCccO.",
    ".OccCCC33CCCccO.",
    ".OcccCC22CCcccO.",
    "O11ccCCCCCCcc11O",
    "O11cC1C11C1Cc11O",
    "O11cCC1CC1CCc11O",
    ".O1ccCCCCCCcc1O.",
    "..OOO3OOOO3OOO..",
    "...O333OO333O...",
)

PALETA_LUMA = {
    "c": hex_to_rgb(0x9B6AE3),  # morado búho
    "1": hex_to_rgb(0x4CA8F0),  # azul plumas
    "2": hex_to_rgb(0x249CB8),  # sombra pico
    "3": hex_to_rgb(0xF5D338),  # amarillo pico/patas
    "C": hex_to_rgb(0xFAF5E7),  # crema pecho
}

LUMA = Personaje(
    id="luma",
    nombre="Luma",
    desc="Búho observador y analista",
    paleta_override=PALETA_LUMA,
    cuerpo=CUERPO_LUMA,
    cara_neutro={6: ".OccC5oCC5oCccO.", 7: ".OccCooCCooCccO.", 8: ".OccCCC33CCCccO."},
    caras={
        "feliz": {5: ".OcccCoCCCCoCccO.", 6: ".OccCo.oCCo.oCccO.", 7: ".OccCooCCooCccO."},
        "cansado": {7: ".OccCooCCooCccO.", 8: ".OccCCC33CCCccO."},
        "pensar": {6: ".OccCC5oCC5oCcO.", 7: ".OccCCooCCooCcO."},
    },
    patas_fila=15,
    paso1=[3, 4, 5, 6, 7],
    paso2=[8, 9, 10, 11, 12],
    brazos_arriba={4: "1OcccCCccCCcccO1", 5: "1OccCCCCCCCCccO1"},
    brazos_tecleo={10: "O11ccCCCCCCcc11O"},
    cara_dormido={7: ".OccCooCCooCccO."},
    cara_leer={7: ".OccC5oCC5oCccO.", 8: ".OccCooCCooCccO."},
    cara_codigo={6: ".OccC5oCC5oCccO.", 7: ".OccCooCCooCccO."},
)

# ---------------------------------------------------------------------------
# 8. MAKO — El gecko ágil
# ---------------------------------------------------------------------------
CUERPO_MAKO = (
    ".OOOO...........",
    "Oc1cO...........",
    "O1OcO...........",
    "OcOOO..OOOOOOO..",
    "O1O...OcccccccO.",
    "OcO..OcccccccccO",
    "O1O..OcccccccccO",
    "OcOOOOcccccccccO",
    "O1cc1ccccccccccO",
    "Occcc1cccccccccO",
    "Oc1ccccc1CCCCcO.",
    ".OccccccCCCCCcO.",
    ".Oc1OOOOcOOOc1O.",
    "Occ1O..OcO.Oc1cO",
    "O111O..O1O.O111O",
    ".OOO...OOO..OOO.",
)

PALETA_MAKO = {
    "c": hex_to_rgb(0x44D0CF),  # turquesa gecko
    "1": hex_to_rgb(0xA6E34B),  # verde lima
    "C": hex_to_rgb(0xF8EFD8),  # crema vientre
}

MAKO = Personaje(
    id="mako",
    nombre="Mako",
    desc="Gecko ágil y adaptable",
    paleta_override=PALETA_MAKO,
    cuerpo=CUERPO_MAKO,
    cara_neutro={5: "OcO..O.5o...5o.O", 6: "O1O..O.oo...oo.O", 8: "OcOOOO...O.O...O", 9: "O1cc1.....O....O"},
    caras={
        "feliz": {5: "OcO..O.oo...oo.O", 6: "O1O..Oo..o.o..oO", 8: "OcOOOO..OOOO...O"},
        "cansado": {6: "O1O..O.oo...oo.O", 8: "OcOOOO...O.O...O"},
        "pensar": {5: "OcO..O..5o...5oO", 6: "O1O..O..oo...ooO"},
    },
    patas_fila=15,
    paso1=[1, 2, 3, 12, 13, 14],
    paso2=[7, 8, 9],
    brazos_arriba={4: "O1O...OcccccccOc"},
    brazos_tecleo={9: "Occcc1cccccccccO"},
    cara_dormido={6: "O1O..O.oo...oo.O"},
    cara_leer={6: "O1O..O.5o...5o.O.", 7: "O1O..O.oo...oo.O."},
    cara_codigo={5: "OcO..O.5o...5o.O", 6: "O1O..O.oo...oo.O"},
)

# ---------------------------------------------------------------------------
# 9. ORBI — El pulpo versátil
# ---------------------------------------------------------------------------
CUERPO_ORBI = (
    "................",
    ".....OOOOOO.....",
    "....O33ccccO....",
    "...O3cccccccO...",
    "...O3cccccccO...",
    "...OccccccccO...",
    "...OccccccccO...",
    "...Occccccc1O...",
    ".OOOccccccc1OOO.",
    "O44Occccccc1O44O",
    "O4Occcccccc11O4O",
    "O4ccccccccccc14O",
    ".Occccccccccc1O.",
    ".OccOccOOccOc1O.",
    "O44OO44OO44OO44O",
    ".OO..OO..OO..OO.",
)

PALETA_ORBI = {
    "c": hex_to_rgb(0xF56B8A),  # coral rosa
    "1": hex_to_rgb(0x87D5F7),  # azul
    "3": hex_to_rgb(0xFFA0B5),  # luz
    "4": hex_to_rgb(0xA98AE8),  # lavanda tentáculos
}

ORBI = Personaje(
    id="orbi",
    nombre="Orbi",
    desc="Pulpo versátil e integrador",
    paleta_override=PALETA_ORBI,
    cuerpo=CUERPO_ORBI,
    cara_neutro={6: "...Oc5o..5occcO.", 7: "...Ocoo..oocccO.", 9: "O44Occ.OO.cc1O44O"},
    caras={
        "feliz": {6: "...Oco....occcO.", 7: "...Oo.o..o.occ1O.", 9: "O44Occ.OO.cc1O44O"},
        "cansado": {7: "...Ocoo..oocccO.", 9: "O44Occ.OO.cc1O44O"},
        "pensar": {6: "...Occ5o..5occO.", 7: "...Occoo..ooccO."},
    },
    patas_fila=15,
    paso1=[1, 2, 9, 10],
    paso2=[5, 6, 13, 14],
    brazos_arriba={8: "4OOOccccccc1OOO4", 9: "444Occccccc1O444"},
    brazos_tecleo={11: "O4ccccccccccc14O"},
    cara_dormido={7: "...Ocoo..oocccO."},
    cara_leer={7: "...Oc5o..5occcO.", 8: "...Ocoo..oocccO."},
    cara_codigo={6: "...Oc5o..5occcO.", 7: "...Ocoo..oocccO."},
)

# ---------------------------------------------------------------------------
# Catálogo y resolución
# ---------------------------------------------------------------------------
CATALOGO: dict[str, Personaje] = {
    "tux": TUX,
    "koru": KORU,
    "clawd": CLAWD,
    "tuno": TUNO,
    "nilo": NILO,
    "brio": BRIO,
    "luma": LUMA,
    "mako": MAKO,
    "orbi": ORBI,
}

LISTA_PERSONAJES = ("tux", "koru", "clawd", "tuno", "nilo", "brio", "luma", "mako", "orbi")

# Compatibilidad con las preferencias anteriores
ALIAS_LEGACY = {
    "naranja": "tux",
    "verde": "nilo",
    "violeta": "luma",
    "rosa": "orbi",
}

def get_personaje(nombre: str) -> Personaje:
    """Devuelve el personaje correspondiente, resolviendo alias si es necesario."""
    nombre = nombre.lower().strip() if nombre else "tux"
    if nombre in ALIAS_LEGACY:
        nombre = ALIAS_LEGACY[nombre]
    return CATALOGO.get(nombre, TUX)

obtener_personaje = get_personaje

