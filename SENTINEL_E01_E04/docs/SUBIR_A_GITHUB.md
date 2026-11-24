# Publicación en GitHub — SENTINEL

Destino del repositorio: `https://github.com/mitchelfalcon/Sentinel_E01_E04`

1. Extraer `SENTINEL_GitHub_Entrega_Final_2026.zip`.
2. Para un repositorio existente, clonar la rama actual y copiar el contenido de la carpeta extraída `SENTINEL_E01_E04/` dentro del clon, sin copiar la carpeta `.git` ni el entorno `.venv`.
3. Inspeccionar cambios; ejecutar desde la raíz `bash scripts/prepare_offline.sh` y `bash scripts/run_all_offline.sh`.
4. Comprobar `python scripts/verify_data_integrity.py` y las evidencias en `evidence/ejecucion_reproducida_2026/`.
5. Confirmar los cambios con Git.

```bash
git clone https://github.com/mitchelfalcon/Sentinel_E01_E04.git
cd Sentinel_E01_E04
# Copia aquí el contenido descomprimido del paquete (sin la carpeta raíz extra).
git status
git add .
git commit -m "Informe UVM final, observaciones 01-12, resultados y reproduccion E01-E04"
git push origin main
```

**Archivos de referencia:** `reports/SENTINEL_Informe_General_Final_2026.pdf`, `reports/SENTINEL_Informe_General_Final_2026.docx`, `docs/INFORME_CIENTIFICO_FINAL_2026.md`, `README.md`, `evidence/ejecucion_reproducida_2026/`.

**Notas de procedencia:** E01–E02 se recalculan de CSV observados; E03 reproduce 120 solicitudes localhost y conserva resultados históricos diferenciados; E04 y E04-S son modelos numéricos reproducidos, no pruebas RF en campo. El video de 60 segundos no se considera publicado hasta añadir el archivo real.
