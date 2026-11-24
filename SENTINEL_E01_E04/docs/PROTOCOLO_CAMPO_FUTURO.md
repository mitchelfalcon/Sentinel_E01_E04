# Protocolo para E04-RF y detector (sin datos de campo atribuidos)

1. Seleccionar MCU, transceptor 915 MHz, modulación/configuración, antenas, ancho de banda, potencia y sensibilidad de fichas técnicas. Confirmar cumplimiento regulatorio local.
2. Elaborar tabla por punto: ID y coordenadas protegidas según riesgo, operador, fecha/hora, distancia y elevación, cobertura útil celular, LOS/NLOS, energía disponible, n.
3. Registrar `run_id`, `seq`, longitud, origen, receptores, salto, timestamp, ACK final, RSSI/SNR, potencia y corriente, versiones y semillas; calibrar relojes para latencia unidireccional.
4. Por cada escenario y distancia registrar PDR, n, IC95 % Wilson, p50/p95 y tasa de reintento. Anotar clima, obstáculos, alturas y polarización.
5. Para detector: dataset etiquetado con consentimiento adulto, TP/FP/TN/FN, sensibilidad, especificidad, falsos positivos por hora y partición de evaluación independiente.
6. Separar estados `GENERADO`, `RECIBIDO`, `ENTREGADO`, `ATENDIDO`. No llamar al C5/911 durante simulaciones.
7. No publicar identidades, ubicación de sobrevivientes, audio personal ni credenciales. Obtener autorizaciones de instalación antes de intervenir infraestructura pública.
