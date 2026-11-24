#!/usr/bin/env python3
"""GEA Latido / E01-E02. HTTP LAN server, stdlib only. Synthetic data only."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE = Path(__file__).resolve().parent
CSV_COLUMNS = ["received_utc", "scenario", "sequence", "bytes", "bits", "sha256", "version", "type"]
CSV_LOCK = threading.Lock()
HEADER = "!BBIIIB6s"  # 21 bytes exactly, authentication bytes NOT implemented.
assert struct.calcsize(HEADER) == 21
MAX_BYTES = 65536
SCENARIOS = {"hot", "cold", "repeater", "mesh", "local", "cli"}


def read_packet(data: bytes):
    if len(data) < 21 or len(data) > MAX_BYTES:
        raise ValueError("La carga debe tener entre 21 y 65536 bytes")
    version, event, pseudo_id, sequence, timestamp, flags, placeholder = struct.unpack(
        HEADER, data[:21]
    )
    if version != 1 or event != 2:
        raise ValueError("Protocolo de laboratorio no reconocido")
    return {"version": version, "type": event, "sequence": sequence,
            "id_ficticio": pseudo_id, "timestamp_emisor": timestamp, "flags": flags}


def make_handler(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_file = data_dir / "gea_recepciones.csv"
    html_file = BASE / "web" / "index.html"

    class Handler(BaseHTTPRequestHandler):
        server_version = "GEA-Latido-Lab/0.2"

        def send_json(self, status, obj):
            result = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(result)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(result)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/health":
                return self.send_json(200, {"ok": True, "nombre": "GEA Latido E01/E02", "internet_requerido": False})
            if path == "/":
                page = html_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                return self.wfile.write(page)
            return self.send_json(404, {"ok": False, "error": "Ruta desconocida"})

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path != "/api/alert":
                return self.send_json(404, {"ok": False, "error": "Ruta desconocida"})
            try:
                raw_length = self.headers.get("Content-Length")
                size = int(raw_length) if raw_length is not None else -1
            except ValueError:
                size = -1
            if size < 21 or size > MAX_BYTES:
                return self.send_json(400, {"ok": False, "error": "Solo 21 a 65536 bytes"})
            data = self.rfile.read(size)
            if len(data) != size:
                return self.send_json(400, {"ok": False, "error": "Carga incompleta"})
            try:
                fields = read_packet(data)
            except ValueError as error:
                return self.send_json(400, {"ok": False, "error": str(error)})
            query = parse_qs(parsed.query)
            scenario = query.get("scenario", ["local"])[0].lower()
            if scenario not in SCENARIOS:
                scenario = "local"
            timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            digest = hashlib.sha256(data).hexdigest()
            row = [timestamp, scenario, fields["sequence"], size, size * 8, digest,
                   fields["version"], fields["type"]]
            with CSV_LOCK:
                needs_header = not csv_file.exists() or csv_file.stat().st_size == 0
                with csv_file.open("a", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    if needs_header:
                        writer.writerow(CSV_COLUMNS)
                    writer.writerow(row)
            print(f"RECIBIDO {timestamp} {scenario=} seq={fields['sequence']} "
                  f"bytes={size} bits={size * 8}", flush=True)
            return self.send_json(200, {"ok": True, "bytes": size, "bits": size * 8,
                                        "sequence": fields["sequence"], "received_utc": timestamp,
                                        "sha256": digest})

        def log_message(self, format, *args):
            # Never print sender IP, device identity, or packet body.
            return

    return Handler


def create_server(host="0.0.0.0", port=8080, data_dir=None):
    return ThreadingHTTPServer((host, port), make_handler(Path(data_dir or BASE / "data")))


def main():
    parser = argparse.ArgumentParser(description="Servidor HTTP LAN para pruebas GEA (SIN SEGURIDAD REAL)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--data-dir", type=Path, default=BASE / "data")
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.data_dir)
    print("GEA LATIDO E01/E02 — SOLO DATOS FICTICIOS / RED LOCAL PRIVADA")
    print(f"Escuchando en http://{args.host}:{server.server_port}/")
    print(f"CSV de recepciones: {(args.data_dir / 'gea_recepciones.csv').resolve()}")
    print("Detener: Ctrl+C", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
