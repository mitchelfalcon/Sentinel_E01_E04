#!/usr/bin/env bash
set -u
printf '\n=== GEA Latido: diagnóstico local (sin escanear redes ajenas) ===\n'
printf '\nFecha:\n'; date -Is
printf '\nInterfaces IPv4 (no compartir públicamente sin revisar):\n'; ip -br -4 addr || true
printf '\nRutas IPv4:\n'; ip -4 route || true
printf '\nRadio Wi-Fi y modo (si está disponible):\n'; iw dev 2>/dev/null || echo 'iw no instalado o sin radio detectable'
printf '\nCapacidad mesh point del adaptador (si existe):\n'; iw list 2>/dev/null | grep -A18 'Supported interface modes' | head -n 20 || true
printf '\nIMPORTANTE: esta lectura NO configura ni altera tu red.\n'
