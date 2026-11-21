#!/usr/bin/env bash
# E01 reproduce transmisión real en la interfaz de loopback Kali (sin internet).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
mkdir -p runs/e01
"$PY" legacy/e01_e02/server.py --host 127.0.0.1 --port 18080 --data-dir runs/e01 > runs/e01/servidor.log 2>&1 &
PID=$!;trap 'kill "$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true' EXIT
sleep .4
"$PY" legacy/e01_e02/client.py --server http://127.0.0.1:18080 --bits 168,336,672,1344,8192 --n 10 --workers 1 --scenario local --output runs/e01/cliente.csv
