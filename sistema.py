"""Reacciones al sistema: batería, música y sonido.

Sin dependencias nuevas: solo stdlib + ``subprocess`` con timeout. Ninguna
función lanza excepciones: si algo no está disponible, devuelve ``None`` o
``False`` y la mascota sigue como si nada.
"""

from __future__ import annotations

import glob
import math
import os
import shutil
import struct
import subprocess
import wave


def bateria():
    """(porcentaje, cargando) o None si no hay batería legible.

    Lee ``/sys/class/power_supply/BAT*/capacity`` y ``status``.
    """
    try:
        for base in sorted(glob.glob("/sys/class/power_supply/BAT*")):
            try:
                with open(os.path.join(base, "capacity"),
                          encoding="utf-8") as fh:
                    pct = int(fh.read().strip())
                try:
                    with open(os.path.join(base, "status"),
                              encoding="utf-8") as fh:
                        status = fh.read().strip()
                except OSError:
                    status = ""
                return (max(0, min(100, pct)),
                        status in ("Charging", "Full"))
            except (OSError, ValueError):
                continue
    except Exception:  # noqa: BLE001
        pass
    return None


def _playerctl(*args, timeout=1):
    """Salida de ``playerctl`` o None si no existe / falla / está vacío."""
    try:
        proc = subprocess.run(
            ["playerctl", *args], capture_output=True, text=True,
            timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    texto = (proc.stdout or "").strip()
    return texto or None


def musica_actual():
    """{"artista", "titulo", "estado"} si suena algo, o None.

    Usa ``playerctl`` (MPRIS): si no está instalado o no hay nada sonando,
    devuelve None sin avisar.
    """
    try:
        estado = _playerctl("status")
        if estado != "Playing":
            return None
        artista = _playerctl("metadata", "artist") or "?"
        titulo = _playerctl("metadata", "title")
        if not titulo:
            return None
        return {"artista": artista, "titulo": titulo, "estado": estado}
    except Exception:  # noqa: BLE001
        return None


def tocar_nota(frecuencia=880, duracion_ms=150):
    """Un pitido sine corto. True si sonó, False si no hay reproductor.

    Genera un WAV en /tmp y lo reproduce con paplay, aplay o ffplay (el
    primero que exista). Silencioso si no hay ninguno.
    """
    try:
        ruta = (f"/tmp/maskot_nota_{int(frecuencia)}"
                f"_{int(duracion_ms)}.wav")
        if not os.path.exists(ruta):
            sr = 22050
            n = max(1, int(sr * max(20, duracion_ms) / 1000.0))
            with wave.open(ruta, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sr)
                frames = bytearray()
                for i in range(n):
                    # Envolvente: sube rápido y cae al final, sin chasquido.
                    env = min(1.0, i / (sr * 0.01)) * min(
                        1.0, (n - i) / (sr * 0.03))
                    v = int(12000 * env
                            * math.sin(2 * math.pi * frecuencia * i / sr))
                    frames += struct.pack("<h", v)
                wav.writeframes(bytes(frames))
        reproductor = (shutil.which("paplay") or shutil.which("aplay")
                       or shutil.which("ffplay"))
        if not reproductor:
            return False
        args = [reproductor, ruta]
        if os.path.basename(reproductor) == "ffplay":
            args += ["-nodisp", "-autoexit", "-loglevel", "quiet"]
        subprocess.run(args, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=5)
        return True
    except Exception:  # noqa: BLE001
        return False
