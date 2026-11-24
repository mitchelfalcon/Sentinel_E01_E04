# SENTINEL | Investigación UVM · E01–E04

**Autoría:** Nailea Mitchel Falcon Triana · **Asesor:** Mtro. Carlos Guadarrama Ponce · **Campus en Línea, ciclo 03-2026.**

Proyecto reproducible de alertas SOS y retransmisión local con proyección a redes Sub-GHz de 915 MHz. Incluye resultados **observados E01–E03**, **simulación E04 semilla 42**, nuevo **estudio de sensibilidad E04-S (LOS/NLOS)**, modelo financiero y corrección de las observaciones 01–12. No se han medido aquí enlaces RF físicos ni desempeño del detector biométrico.

## Documentos de entrega

- [Informe general final (Markdown)](docs/INFORME_CIENTIFICO_FINAL_2026.md)
- [Informe general PDF](reports/SENTINEL_Informe_General_Final_2026.pdf)
- [Informe editable Word](reports/SENTINEL_Informe_General_Final_2026.docx)
- [Respuestas a las 12 observaciones](docs/OBSERVACIONES_01_12_CORREGIDAS.md)
- [Resultados y procedencia](docs/RESULTADOS_Y_PROCEDENCIA.md)
- [Cómo reproducir las ejecuciones](docs/REPRODUCIR_EJECUCIONES.md)
- [Protocolo de campo y detector](docs/PROTOCOLO_CAMPO_FUTURO.md)
- [Presupuesto paramétrico CAPEX/OPEX](docs/FINANZAS_MODELO_PILOTO.md)

## Reproducción

```bash
bash scripts/prepare_offline.sh
bash scripts/run_all_offline.sh
python scripts/verify_data_integrity.py
```

Python 3.10+; sin dependencias externas para código y pruebas. Windows: `scripts/prepare_offline.ps1`, `scripts/run_all_offline.ps1` (ver compatibilidad para el benchmark local de procesos). Los gráficos de referencia ya están incluidos.

## Evidencia verificada

- `data/observados/`: CSV originales E01 y E02 con manifiesto SHA-256.
- `evidence/ejecucion_reproducida_2026/`: salida real de pruebas, reanálisis E01/E02, benchmark local E03 120 envíos, E04 100 alertas y E04-S 2,000 intentos sintéticos.
- `figures/`: gráficos académicos y diseño conceptual del arete (no dispositivo construido).

| Etapa | Confirmaciones | RTT/tiempo p50 | p95 | Procedencia |
|---|---|---|---|---|
| E01 | 50/50 | 1.05 ms | 2.50 ms | CSV original, HTTP local |
| E02 HOT | 50/50 | 26.00 ms | 48.20 ms | CSV original, Safari/LAN |
| E03 original directa | 60/60 | 1.07 ms | 1.90 ms | Informe anterior |
| E03 original 2 relés | 60/60 | 4.11 ms | 7.54 ms | Informe anterior |
| E04 simulación | 97/100 | 44.96 ms | 67.48 ms | Modelo discreto; semilla 42 |

**Meta en campo:** PDR ≥95 % y latencia hasta ACK final <2.5 s; sin afirmación de validación RF. La confirmación humana de atención es diferente del ACK técnico.

**Video de 60 s:** pendiente de publicar en este repositorio, sin enlace inventado.

![Código QR hacia repositorio GitHub](figures/QR_GITHUB_SENTINEL.png)

**Fuentes institucionales proporcionadas:** `docs/referencias/estadisticas_bcs_imagenes_proporcionadas/` (cifras usadas según sus periodos reportados; no sustituye diagnóstico de cobertura).
