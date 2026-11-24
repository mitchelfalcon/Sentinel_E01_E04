$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$p = '.\.venv\Scripts\python.exe'
& $p -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Pruebas sentinel fallaron' }
$env:PYTHONPATH = (Resolve-Path 'legacy/e01_e02').Path
& $p -m unittest discover -s legacy/e01_e02/tests -v
if ($LASTEXITCODE -ne 0) { throw 'Pruebas E01/E02 fallaron' }
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
& $p legacy/e03/code/selftest_e03_v2.py
& $p -m sentinel.analyze --out runs/estadisticas_observadas.json
& $p scripts/benchmark_e03_local.py --output-dir runs/e03_repeticion
& $p -m sentinel.mesh_sim --seed 42 --count 100 --fail-after 50 --output runs/e04_simulacion.csv
& $p -m sentinel.distance_model --seed 20261123 --n 200 --output-dir runs/e04_sensibilidad
& $p scripts/generate_figures.py
Write-Host 'SENTINEL: pruebas, resultados y modelo E04 completados en runs/'
