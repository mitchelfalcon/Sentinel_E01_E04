#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[ -x "$PY" ] || { echo "Primero bash scripts/prepare_offline.sh"; exit 2; }
mkdir -p runs
"$PY" -m unittest discover -s tests -v
PYTHONPATH="$(pwd)/legacy/e01_e02" "$PY" -m unittest discover -s legacy/e01_e02/tests -v
"$PY" legacy/e03/code/selftest_e03_v2.py
"$PY" -m sentinel.analyze --out runs/estadisticas_observadas.json >/dev/null
"$PY" -m sentinel.mesh_sim --seed 42 --count 100 --fail-after 50 --output runs/e04_simulacion.csv
"$PY" scripts/generate_figures.py
echo "SUITE FINALIZADA. Resultados en runs/ y figuras en figures/"
