#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo "Python3 no encontrado (instalar antes de aislar red)";exit 2; }
python3 -m venv .venv
.venv/bin/python --version
echo "Entorno offline preparado: .venv/bin/python; sin pip ni descargas"
