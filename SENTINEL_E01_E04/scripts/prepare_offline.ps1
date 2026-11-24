$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
py -3 -m venv .venv
.\.venv\Scripts\python.exe --version
Write-Host 'Listo: entorno offline sin paquetes externos'
