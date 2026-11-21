# Programa experimental E01-E04 | SENTINEL / GEA Latido

## Definiciones de resultado y procedencia

- **OBSERVADO:** registro instrumental presente en `data/observados/`.
- **REPRODUCIBLE LOCAL:** ejecución real sobre loopback entre procesos; no demuestra red inalámbrica.
- **ENSAYO RF:** solo si existen radios compatibles, topología, registros independientes por radio y archivos de campo.
- **SIMULADO:** estimaciones deterministas en `sentinel/mesh_sim.py`, no resultados físicos.

## E01. Referencia loopback

**Pregunta:** ¿el formato y servicio procesan sin errores el conjunto de tamaños?
**Entrada:** 168/336/672/1344/8192 bits, 10 envíos por tamaño, 127.0.0.1.
**Procedimiento:** `bash scripts/e01_loopback.sh`.
**Evidencias:** `runs/e01/cliente.csv`, `runs/e01/gea_recepciones.csv`, bitácora, tests.
**Variables:** tamaño; RTT HTTP; confirmación, hash.

## E02. iPhone real Wi-Fi/LAN

**HOT:** Kali Ethernet al router, iPhone en la misma LAN; `python legacy/e01_e02/server.py --host IP_KALI --port 8080 --data-dir runs/e02_hot`; iPhone Safari `http://IP_KALI:8080`, datos celulares apagados. `sudo tcpdump -ni eth0 'tcp port 8080'` con datos sintéticos; restringir firewall a IP origen. Guardar CSV Safari, servidor y traza; comprobar 50 ACK finales.

**COLD:** documentar modo anterior del Steren, sin WAN y aislado del ZTE; Kali cable al puerto LAN del Steren en modo Router; iPhone al Wi-Fi del Steren. Comprobar acceso local `/health` y fracaso de acceso externo con datos móviles apagados. Hacer 10 repeticiones por cada longitud. Restaurar reglas UFW y router. **El nombre COLD dentro del selector de Safari no es evidencia del aislamiento.**

## E03. Mini-servidores de aplicación (A → B → C)

En Kali C: `python legacy/e03/code/gea_node.py --role sink --node C --host IP_C --port 8080 --log runs/e03_C.csv`. En computadora B: `python legacy/e03/code/gea_node.py --role relay --node B --host IP_B --port 8081 --next http://IP_C:8080 --log runs/e03_B.csv`. En iPhone abrir `http://IP_B:8081` y enviar `LUNA` (ficticio). Guardar los tres CSV, evidencia de las tres MAC/IP internas anonimizada, ACK, SHA-256 y ruta B>C. Comprobar con un control de envío directo A→C. **E03 prueba retransmisión de aplicación; no obliga a múltiples saltos RF si comparte el mismo AP.**

Prueba de código local: `python legacy/e03/code/selftest_e03_v2.py`; dos relays son procesos de una misma máquina, no radios físicos.

## E04. Sub-GHz / mesh multi-hop y cuatro fases

**Arquitectura:** A (emisor) → B (radio-relay) → C (estación). En una segunda ruta A → D → C, apagar B para comprobar recuperación. Al menos tres radios compatibles con capacidad real de retransmisión y topología documentada; cuatro si se estudian rutas alternativas. El router COM-852 no demuestra por sí solo LoRa ni 802.11s.

**Cuatro estados del SOS:** `GENERADO`, `RECIBIDO` (primer nodo), `ENTREGADO` (estación), `ATENDIDO_SIMULADO` (operador de prueba). La fase humana no es ACK de red.

**Plan de campo:** 0, 100, 250, 500, 1000 m si terreno/alcance permite, añadir 2500 y 5000 m solo donde técnicamente sea razonable. Registrar LOS/NLOS, terreno, obstáculos, altura de antenas, modelo y firmware del radio, potencia EIRP conforme a regulación aplicable, SF/BW/CR si LoRa, RSSI/SNR, relojes, hash, número de saltos y ACK. Para PDR cada condición ≥100 envíos y ≥3 rondas cuando sea viable; IC95 % binomial Wilson. No usar víctimas reales ni emergencias activas.

**Prueba de ruta real:** aislar A de C por RF y/o filtrar enlace directo con hardware y verificación independiente; logs de B reciben paquete y C recibe reenvío posterior con mismo hash y secuencia. Medir ruta alternativa y pérdida cuando B se apaga, con hora y ACK por nodo. Confirmar falla y recuperación; no llamar mesh a mera transmisión a un único AP.

**Medición temporal:** RTT con reloj monotónico del emisor evita sincronización. Para latencia unidireccional, NTP/PPS o instrumentación común verificada y registrando incertidumbre; nunca restar relojes no sincronizados. Meta futura PDR≥95% y latencia extremo a extremo <2.5s.

**Radio a software:** el módulo `sentinel.verify_rf` valida el formato de CSV de los nodos y hash declarados, pero la retransmisión RF necesita firmware/radios seleccionados. CSV de plantilla: `data/plantillas/e04_rf_log_template.csv`.

**Simulator offline:** `python -m sentinel.mesh_sim --seed 42 --count 100 --fail-after 50` genera registros marcados `SIMULADO_NO_RF`.

**Calcular presupuesto de enlace:** FSPL(dB)=32.44+20log10(d_km)+20log10(f_MHz), con d>0. FSPL a 915 MHz aprox 91.7 dB (1 km), 99.6 dB (2.5 km), 105.6 dB (5 km), 115.2 dB (15 km); es solo límite ideal LOS. Margen real=PTx+GTx+GRx−pérdidas−sensibilidad; completar ficha técnica antes de afirmar alcance.

## Falsación y análisis

Se compararán ruta directa, 2 saltos RF, interrupción de B, alternativa D, HOT/COLD y tamaño. Se reportarán PDR, IC95 % Wilson, p50/p95, duplicados, tiempo de recuperación, % de ACK por fase, hash, distancia, consumo y variabilidad entre sitios, con IC95 %. Si el mensaje no llega, se registra como no entregado; no inferir rescate.

## E04. Modo UART por radios transparentes en banco (Linux/macOS)

Se incorpora `sentinel/uart_mesh.py` con codificador de 21 bytes, CRC de carga y trama, TTL, log por equipo, ACK del primer receptor, ACK de estación y entrada manual `atender <secuencia>`. Usa **solo Python estándar**, puerto serial UART y radios capaces de transportar líneas base64 transparentes sin modificar datos. **No selecciona configuración de LoRa ni automatiza el mesh; cada radio necesita firmware/configuración compatible.** La trama física de ejemplo ocupa 33 bytes binarios antes de base64/UART/radio, no solo 21 bytes.

Montaje hipotético para tres equipos Linux con radios configurados de forma compatible y en una banda/región legalmente habilitada (confirmar homologación, potencia, frecuencia y derechos de uso):

Terminal estación C: `./.venv/bin/python -m sentinel.uart_mesh --role sink --node C --device /dev/ttyUSB0 --baud 9600 --radio-model MODELO --firmware VERSION --duration 90 --log runs/e04_C.csv`

Terminal relay B: `./.venv/bin/python -m sentinel.uart_mesh --role relay --node B --device /dev/ttyUSB0 --baud 9600 --radio-model MODELO --firmware VERSION --duration 90 --log runs/e04_B.csv`

Terminal emisor A: `./.venv/bin/python -m sentinel.uart_mesh --role source --node A --device /dev/ttyUSB0 --baud 9600 --radio-model MODELO --firmware VERSION --n 10 --interval 2 --duration 40 --log runs/e04_A.csv`

La estación C descarta la recepción directa A→C de hop=0; esto es un control lógico, **no demuestra por sí solo aislamiento RF**. Probar que el radio C no recibe A sin relay B y documentar con capturas de radio/log; confirmar RX en B y C, secuencia y SHA-256. Para ruta D, repetir con B apagado y D como relay activo; se trata de conmutación experimental de ruta, no de autodescubrimiento mesh a menos que el firmware radio lo pruebe. El operador en C escribe `atender 1` para registrar confirmación humana ficticia.

Ejecutar `./.venv/bin/python -m sentinel.verify_rf runs/e04_C.csv` y guardar logs A/B/C (el validador de saltos necesita un CSV combinado con los registros de todos los radios para demostrar ≥2 RX hops). Unir los CSV conservando cabecera una sola vez, o usar un analizador posterior de campo. No publicar ubicaciones privadas, claves ni datos reales.
