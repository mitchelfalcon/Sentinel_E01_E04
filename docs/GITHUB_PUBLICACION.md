# Repositorio reproducible: publicación y trabajo offline

## Primero offline

Extraer el ZIP en Kali o Windows. Kali: `bash scripts/prepare_offline.sh` y `bash scripts/run_all_offline.sh`; Windows PowerShell: `./scripts/prepare_offline.ps1` y `./scripts/run_all_offline.ps1`. **Las pruebas locales se ejecutan sin internet.** Para E02 y E03 físicos, conectar solo la LAN privada. E04 `simulate` no reemplaza radios de campo.

## Publicar con Git (requiere conexión y permisos)

Crear un repositorio GitHub nuevo y vacío, nombre sugerido `SENTINEL-GEA-Latido-E01-E04`, sin generar README externo. En la raíz local ejecutar:

```bash
git init
git branch -M main
git add .
git status --short
git diff --cached --stat
git commit -m "Initial reproducible SENTINEL E01-E04 laboratory package"
git remote add origin https://github.com/USUARIO/SENTINEL-GEA-Latido-E01-E04.git
git push -u origin main
```

Sustituir USUARIO. Nunca pegar tokens en scripts o README. Si Github solicita login usar credential helper o SSH ya configurado. `git push` NO funciona sin internet; `git commit` sí. Para USB y transporte offline: `git bundle create sentinel.bundle --all` (después de commit).

## Publicar con el conector GitHub (MCP)

Con el conector de GitHub de ChatGPT: indicar el destino exacto `usuario/repositorio` y autorizar la creación del repositorio/commit. El archivo ZIP es el paquete de entrega y los archivos de código se deben publicar descomprimidos, no únicamente como ZIP. Antes de publicar verificar `git status`, `docs/PRIVACIDAD_ETICA.md` y las rutas ignoradas. No se publicarán capturas de datos privados.

## Verificación independiente

`bash scripts/prepare_offline.sh && bash scripts/run_all_offline.sh` (Python 3.10+); los test E01 y E03 en local comprueban código y los datos observados se analizan sin red. Los experimentos RF E04 son ejecutables únicamente cuando se conecten radios compatibles y se documenten los registros instrumentales.
