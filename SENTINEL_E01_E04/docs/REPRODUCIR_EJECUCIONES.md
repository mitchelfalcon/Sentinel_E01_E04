# Cómo reproducir los resultados SENTINEL

La ejecución del paquete utiliza solo Python 3.10+ y biblioteca estándar. Ejecútese desde la raíz del repositorio. No envía alertas reales ni realiza pruebas Sub-GHz.

```bash
bash scripts/prepare_offline.sh
bash scripts/run_all_offline.sh
python scripts/verify_data_integrity.py
```

**Archivos generados:** `runs/estadisticas_observadas.json`, `runs/e03_repeticion/{envios_120.csv,resumen.json}`, `runs/e04_simulacion.csv`, `runs/e04_simulacion.summary.json`, `runs/e04_sensibilidad/{eventos_modelados.csv,pdr_por_distancia.csv,configuracion.json}`.

**Copia congelada para publicar:** `evidence/ejecucion_reproducida_2026/` con sumas SHA-256 y log de 16 pruebas. El tiempo RTT depende del hardware. Las semillas hacen determinista E04 y E04-S, no las mediciones HTTP.

**Etiquetas obligatorias:** `OBSERVADO_HTTP_LOCAL` para E01–E03, `SIMULADO_NO_RF` para E04, `E04-S_PARAMETRICO_NO_RF` para sensibilidad. No combinar tiempos entre categorías.
