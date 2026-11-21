$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$p = '.\.venv\Scripts\python.exe'
& $p -m unittest discover -s tests -v
$env:PYTHONPATH = (Resolve-Path 'legacy/e01_e02').Path
& $p -m unittest discover -s legacy/e01_e02/tests -v
& $p legacy/e03/code/selftest_e03_v2.py
& $p -m sentinel.analyze
& $p -m sentinel.mesh_sim --seed 42 --count 100 --fail-after 50
& $p scripts/generate_figures.py
