"""API HTTP local para controlar la mascota.

- Solo escucha en 127.0.0.1 (nunca en 0.0.0.0) y **apagada por defecto**: hay
  que activarla desde el menú de la bandeja.
- Sin dependencias externas: `http.server` de la biblioteca estándar, en un
  hilo aparte.

Rutas:
    GET  /estado      -> instantánea del estado (JSON)
    GET  /rutinas     -> catálogo de rutinas
    POST /aviso       -> {"texto": "..."}          aviso corto en el globo
    POST /decir       -> {"texto": "...", "ms": 4000}
    POST /rutina      -> {"nombre": "pasear"}
    POST /pomodoro    -> {"accion": "iniciar|pausar|reanudar|saltar|parar",
                          "formato": "25/5"}

Diseño importante: el hilo HTTP **nunca** toca GTK. Los POST se encolan y los
procesa el bucle principal de GLib (`GLib.idle_add`); los GET leen una
instantánea que el bucle principal va actualizando.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PUERTO_POR_DEFECTO = 7777
HOST = "127.0.0.1"
CUERPO_MAX = 64 * 1024


class ApiLocal:
    """Servidor HTTP local de la mascota (apagado por defecto)."""

    def __init__(self, proveedor_estado, manejador_acciones, puerto=PUERTO_POR_DEFECTO,
                 log=print):
        """`proveedor_estado()` -> dict; `manejador_acciones(nombre, datos)` -> str."""
        self.proveedor_estado = proveedor_estado
        self.manejador_acciones = manejador_acciones
        self.puerto = puerto
        self.log = log
        self._servidor = None
        self._hilo = None
        self.activo = False

    # -- ciclo de vida -------------------------------------------------------

    def arrancar(self):
        if self.activo:
            return True
        api = self

        class Manejador(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, formato, *args):      # silencia el log de stdlib
                pass

            def _responder(self, codigo, objeto):
                cuerpo = json.dumps(objeto, ensure_ascii=False).encode("utf-8")
                self.send_response(codigo)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(cuerpo)))
                self.end_headers()
                self.wfile.write(cuerpo)

            def do_GET(self):                            # noqa: N802 (stdlib)
                ruta = urlparse(self.path).path.rstrip("/") or "/"
                if ruta == "/estado":
                    self._responder(200, api.proveedor_estado())
                elif ruta == "/rutinas":
                    self._responder(200, api.manejador_acciones("listar_rutinas", {}))
                else:
                    self._responder(404, {"error": f"ruta desconocida: {ruta}"})

            def do_POST(self):                           # noqa: N802 (stdlib)
                ruta = urlparse(self.path).path.rstrip("/") or "/"
                try:
                    largo = int(self.headers.get("Content-Length") or 0)
                except ValueError:
                    largo = 0
                if largo > CUERPO_MAX:
                    self._responder(413, {"error": "cuerpo demasiado grande"})
                    return
                crudo = self.rfile.read(largo) if largo else b"{}"
                try:
                    datos = json.loads(crudo.decode("utf-8") or "{}")
                except (ValueError, UnicodeDecodeError):
                    self._responder(400, {"error": "JSON inválido"})
                    return
                if not isinstance(datos, dict):
                    self._responder(400, {"error": "se esperaba un objeto JSON"})
                    return

                acciones = {
                    "/aviso": "aviso",
                    "/decir": "decir",
                    "/rutina": "rutina",
                    "/pomodoro": "pomodoro",
                }
                accion = acciones.get(ruta)
                if accion is None:
                    self._responder(404, {"error": f"ruta desconocida: {ruta}"})
                    return
                resultado = api.manejador_acciones(accion, datos)
                if isinstance(resultado, tuple):
                    codigo, objeto = resultado
                else:
                    codigo, objeto = 200, {"ok": resultado}
                self._responder(codigo, objeto)

        try:
            servidor = ThreadingServer((HOST, self.puerto), Manejador)
        except OSError as exc:
            self.log(f"[api] no se pudo arrancar en {HOST}:{self.puerto}: {exc}")
            return False
        servidor.daemon_threads = True
        self._servidor = servidor
        self._hilo = threading.Thread(target=servidor.serve_forever,
                                      kwargs={"poll_interval": 0.2},
                                      daemon=True, name="api-http")
        self._hilo.start()
        self.activo = True
        self.log(f"[api] escuchando en http://{HOST}:{self.puerto} "
                 "(GET /estado, /rutinas; POST /aviso, /decir, /rutina, /pomodoro)")
        return True

    def parar(self):
        if not self.activo or self._servidor is None:
            return False
        self._servidor.shutdown()
        self._servidor.server_close()
        self._servidor = None
        self._hilo = None
        self.activo = False
        self.log("[api] servidor detenido")
        return True

    def alternar(self):
        if self.activo:
            self.parar()
            return False
        self.arrancar()
        return self.activo

    def estado(self):
        return {
            "activa": self.activo,
            "url": f"http://{HOST}:{self.puerto}" if self.activo else None,
        }


class ThreadingServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
