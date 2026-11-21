# GEA Latido | E03 v2 · Guía de campo offline

**UVM · Fase II · No es un sistema de emergencias.** Antes de desconectar internet, descarga este archivo en ambas computadoras. Todos los números IP utilizados en los ejemplos deben sustituirse por los que se vean en las pantallas reales.

## Objetivo

Demostrar que **iPhone A → Laptop B (relay) → Kali C (destino)** transmite bytes binarios reales a través de dos equipos ejecutando Python, en una LAN independiente de internet. Se registran la identidad ficticia `LUNA`, seis tamaños de carga, RTT, cantidad de envíos, SHA-256 y CRC32, ruta de aplicación, secuencia y tasa de entrega. B es un **relay de aplicación**; todavía **no** se demuestra un salto de radio 802.11s/EasyMesh.

## Qué descargar ANTES de salir de internet

- **Kali**: este ZIP (`GEA_E03_V2_Kit_Offline_UVM.zip`), que contiene `code/gea_node.py`, `code/selftest_e03_v2.py`, `code/send_probe.py`, `code/analyze_e03.py` y esta guía. Python 3.10+ y `unzip`; no hay `pip install` ni requisitos de nube.
- **Laptop B si tiene Windows**: Python 3.10+ desde [python.org/downloads](https://www.python.org/downloads/), solo si no lo tiene instalado. Verificar en PowerShell `py -3 --version`. Copiar este ZIP a B o por memoria USB. No necesita Kali Linux.
- **Laptop B si tiene Linux/macOS**: comprobar `python3 --version`. Si falta Python, instalarlo **antes** de dejar la red online.
- **iPhone 17**: **nada**. Safari es el cliente. Guardar el PDF anterior y esta guía en Archivos, y desactivar datos celulares para la ejecución COLD.

No instalar MCP, Kaggle, Docker ni servidores FTP; ninguno mejora esta prueba.

## Cambios respecto a la versión E03 inicial

**No mezclar `gea_node.py` de la versión anterior con esta versión 2.** El protocolo binario mínimo ahora incluye `LUNA` dentro de sus **21 bytes**, no solo como cabecera HTTP.

| Byte(s) | Datos | Total |
|---|---|---:|
| 0 | versión 2 | 1 |
| 1 | tipo 3 (ensayo) | 1 |
| 2–7 | alias ficticio ASCII (hasta 6 caracteres, relleno cero) | 6 |
| 8–11 | secuencia | 4 |
| 12–15 | timestamp UTC UNIX | 4 |
| 16 | indicadores | 1 |
| 17–20 | CRC32 sobre los primeros 17 bytes | 4 |
| **Total** | **Carga útil mínima** | **21 bytes / 168 bits** |

Para cargas mayores, se añade relleno entre indicadores y los últimos cuatro bytes de CRC32. El receptor comprueba CRC32 y registra SHA-256 de la carga íntegra. **Ni CRC32 ni SHA-256 sin clave equivalen a autenticación o cifrado.** No enviar nombres ni audios reales.

## 1. Topología física — COLD

```text
                  STEREN COM-852 — ROUTER (WAN SIN CABLE)
                         ┌──────────────────────────┐
 iPhone 17 A ─── Wi-Fi ──┤                          ├── cable LAN ── Kali Linux C
 Laptop B    ── Wi-Fi ──┤                          │   8080 / receptor
                         └──────────────────────────┘
 iPhone A ---- POST ----> Laptop B:8081 ---- POST ----> Kali C:8080
                       Ruta reportada: B > C
```

El Infinitum original permanece encendido, pero **ningún enlace de Steren** (WAN ni WISP ni repetidor) debe conectarlo al Infinitum durante E03-COLD. Documentar con fotos la conexión original del Steren antes de cambiar su modo. Un solo equipo con dos procesos NO prueba relay físico; aquí B y C deben ser computadoras distintas.

## 2. Inspección y autoprueba, todavía CON internet

En Kali:

```bash
mkdir -p ~/proyectos/GEA_Latido/GEA_E03_V2_Offline
cd ~/proyectos/GEA_Latido/GEA_E03_V2_Offline
# Descargar ZIP del chat y extraerlo a esta carpeta con unzip o gestor gráfico
python3 -m venv .venv
source .venv/bin/activate
python code/selftest_e03_v2.py
```

Resultado esperado: `OK E03v2: 6 longitudes ...`. **Esta prueba usa procesos locales solamente**. En B comprobar Python. **Windows:** abrir PowerShell en la carpeta extraída y ejecutar `py -3 --version`. **Linux:** `python3 --version`. **macOS:** `python3 --version`.

## 3. Cambiar al Steren y descubrir IP

1. Guarda toda evidencia de E01/E02, detén los servidores anteriores con `Ctrl+C`, conserva copias de los CSV.
2. Con el manual E02 COLD a mano: Steren en modo **Router** con DHCP LAN y Wi-Fi privado, puerto WAN sin conectar. No usar modo Repetidor Universal ni WISP para esta prueba.
3. Mueve **solo** el cable Ethernet de Kali al **puerto LAN** del Steren. La laptop B y el iPhone se conectan por **Wi-Fi** del Steren. Desactivar datos celulares del iPhone, VPN y servicios de tethering. No se apaga Infinitum.
4. Comprueba IP y gateway. Kali `ip -4 -br addr show eth0; ip -4 route`. B Linux `ip -4 -br addr`; B Windows `ipconfig`. En el iPhone `Configuración → Wi-Fi → ⓘ → Dirección IP`. Todas deben estar en la misma subred.
5. Escribe en tu bitácora IP de A, B y C y fecha/hora. **Usa estas IP en todos los comandos**, no los valores de ejemplo de esta guía.

### Plan de recuperación si Kali no obtiene IP

En Kali: `nmcli device status`, `sudo nmcli device disconnect eth0`, `sudo nmcli device connect eth0`, `ip -4 -br addr show eth0`. Si sigue sin IP, revisa que el cable llegue a LAN del Steren y su DHCP esté habilitado. **No modifiques los ajustes globales del cortafuegos ni reinicies Infinitum.** Si no puedes entrar al Steren, vuelve al estado físico anterior con la última sección de esta guía y revisa sus ajustes cuando recuperes internet.

## 4. Reglas de firewall: abrir solo lo necesario

**Ejemplo** (¡sustituye IP!): C Kali = `192.168.0.100` en `eth0`; B laptop = `192.168.0.101`; A iPhone = `192.168.0.102`.

En Kali, inspeccionar reglas antes: `sudo ufw status numbered`. Si UFW está activo, autoriza **solo IP de B a puerto 8080**:

```bash
sudo ufw allow in on eth0 from 192.168.0.101 to any port 8080 proto tcp
sudo ufw status numbered
```

Si existe una regla temporal anterior que permite a **toda** la subred entrar al puerto 8080, evalúa retirarla por su sintaxis exacta antes de declarar que solo B puede acceder. **No** ejecutar `ufw disable`, `iptables -F`, `nft flush ruleset` ni abrir puertos desde WAN del router.

En **B Windows**, abre PowerShell **como administrador** y ejecuta, usando IP real del iPhone y con confianza en esa red local:

```powershell
New-NetFirewallRule -DisplayName 'GEA-E03-LAB-8081' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8081 -RemoteAddress 192.168.0.102 -Profile Any
```

Al terminar eliminar esta excepción: `Remove-NetFirewallRule -DisplayName 'GEA-E03-LAB-8081'`. Usa solo este nombre para evitar tocar otras reglas. En **B Linux**, si usa UFW activo, permite TCP 8081 únicamente desde IP de A y luego revierte exactamente la excepción. En macOS revisa ajustes de cortafuegos de aplicaciones, sin deshabilitarlo globalmente.

## 5. Inicia el DESTINO C en Kali (terminal 1)

```bash
cd ~/proyectos/GEA_Latido/GEA_E03_V2_Offline
source .venv/bin/activate
mkdir -p data
python -u code/gea_node.py --role sink --node C --host 192.168.0.100 --port 8080 --log data/e03_nodo_C.csv 2>&1 | tee data/e03_C_terminal.log
```

**Sustituir `192.168.0.100` por IP real de C.** Esta terminal queda escuchando: NO se cierra. En el propio Kali verificar `curl http://IP_C_REAL:8080/health`.

## 6. Inicia el MINI-SERVIDOR B en la segunda laptop (terminal 2 de B)

Copia **la carpeta `code/` completa** a la laptop B y ejecútala desde la carpeta raíz del kit. **Sustituye ambas IP**: la que sigue a `--host` es la de B; la que sigue a `--next` es la de Kali C.

**Si B es Windows (PowerShell):**

```powershell
py -3 code\gea_node.py --role relay --node B --host 192.168.0.101 --port 8081 --next http://192.168.0.100:8080 --log data\e03_nodo_B.csv
```

**Si B es Linux/macOS:**

```bash
python3 code/gea_node.py --role relay --node B --host 192.168.0.101 --port 8081 --next http://192.168.0.100:8080 --log data/e03_nodo_B.csv
```

Si Windows no tiene `py`, prueba `python --version` y sustituye `py -3` por `python`. Comprueba en navegador de B `http://127.0.0.1:8081/health`; desde B comprueba destino `http://IP_C_REAL:8080/health`. Si B responde 502, lo más frecuente es un error de IP de destino o regla UFW de Kali.

## 7. Emisor A: iPhone 17, Safari

1. Conectar iPhone al **mismo SSID Steren** que B, con datos celulares apagados. Si iOS indica «Sin acceso a internet», elegir permanecer en la red.
2. Safari: abrir **`http://IP_REAL_B:8081/`**. **No usar IP de Kali**, porque eso evitaría el relay B.
3. Escribir **alias ficticio `LUNA`**. Seleccionar `168 bits`, `10 repeticiones`, ID `E03_FIS1_OFFLINE` y pulsar «Enviar».
4. Debe aparecer la ruta **`B>C`** y en ambas terminales deberían aparecer mensajes con `LUNA` y el mismo SHA-256. Comparar secuencia y número de bytes.
5. Repetir con `336, 672, 1344, 8192, 32768 bits`, 10 repeticiones cada uno. Guardar `GEA_E03_iPhone_alias.csv` desde Safari. Se puede repetir tres veces por escenario para estimar variabilidad temporal.

**Este ensayo prueba una retransmisión física entre laptops a nivel de aplicación.** El radio del Steren puede entregar A→B y B→C usando sus medios habituales; no estamos verificando selección de caminos 802.11s ni distintos saltos RF.

## 8. Comparación directa (control)

Para comparar **A→C directo** vs **A→B→C**, agrega temporalmente en Kali acceso TCP 8080 solo desde la IP del iPhone, selecciona otro ID de ensayo `E03_DIRECTO` en Safari y abre directamente `http://IP_C_REAL:8080/`. El navegador recibirá la ruta `C` en vez de `B>C`. Realiza las seis cargas con igual cantidad de repeticiones y ubicación. **Elimina inmediatamente** la excepción temporal para IP del iPhone antes de las pruebas posteriores por relay B.

No mezclar datos directos y retransmitidos en una sola media. Registrar distancia, obstáculos, uso de CPU y RSSI si se puede medir con las herramientas disponibles.

## 9. Prueba de falla (controlada)

Mientras A→B→C funciona, detener **solo servidor C** con `Ctrl+C`; B seguirá encendido pero mostrará error o 502. Registrar 10 intentos fallidos. Reiniciar C y repetir el lote con otro ID `E03_RECUPERACION`. **El sistema actual NO descubre automáticamente una alternativa**, eso es la hipótesis de E04.

## 10. Analizar resultados offline

Copiar CSV de Safari (iPhone → Archivos → compartir por USB/AirDrop si compatible o al reconectar) y archivo CSV de B a Kali. Después, ya reunidos los tres CSV:

```bash
python3 code/analyze_e03.py --safari data/GEA_E03_iPhone_alias.csv --b data/e03_nodo_B.csv --c data/e03_nodo_C.csv --output data/e03_resumen.csv
```

Revisa si en cada carga las filas entregadas tienen coincidencia de **alias, secuencia, bits y SHA-256** en B y C. Atención: la interfaz Safari puede seguir acumulando resultados al cambiar tamaños; anota el ID de ensayo para distinguir sesiones.

## 11. Volver a la configuración original

- Detén B y C (`Ctrl+C`), guarda `data/e03_nodo_B.csv`, `data/e03_nodo_C.csv`, CSV Safari, logs, fotos y IP.
- Si abriste UFW en Kali para B, elimina **exactamente** esa regla (IP real), por ejemplo:

```bash
sudo ufw delete allow in on eth0 from 192.168.0.101 to any port 8080 proto tcp
```

- Si abriste regla en Windows B: `Remove-NetFirewallRule -DisplayName 'GEA-E03-LAB-8081'` como administrador; si fue UFW Linux, elimina su equivalente exacto.
- Devuelve el cable Ethernet de Kali al puerto original LAN Infinitum; en Kali:

```bash
sudo nmcli device disconnect eth0
sudo nmcli device connect eth0
ip -4 -br addr show eth0
ip -4 route
```

- Vuelve a conectar B y iPhone a sus Wi-Fi habituales. **Restaura modo, SSID y credenciales originales del Steren mediante su panel y las fotos/backup previos**. Los comandos de Kali no restauran automáticamente los parámetros del Steren. No hacer factory reset salvo necesidad y posibilidad de reconfiguración.

## 12. Qué debemos conseguir para E04: mesh RF genuina

- Como mínimo **tres radios/nodos mesh compatibles** (preferentemente Linux 802.11s, chipsets y controladores comprobados) y un punto de entrada Wi-Fi convencional para iPhone, o una solución documentada con firmware EasyMesh que permita verificar enlaces entre nodos.
- En E04 el teléfono **no tiene por qué implementar 802.11s**: se conecta al gateway AP; los nodos mesh forman el backbone offline.
- Reusar **el mismo protocolo de 21 bytes de E03** sobre la red mesh, pero añadir numeración por enlace y trazas de rutas de red; `batctl n`, `batctl o` y capturas en nodos compatibles si se utiliza BATMAN-adv.
- Diseñar A → B → C como ruta forzada sin enlace directo A→C, y posteriormente A → D → C como ruta alternativa. Documentar fallo/reconexión con métricas, RSSI, latencia p50/p95, tasa de entrega, consumo y alcance.
- Aclaración: **ZTE EasyMesh y Steren en modo repetidor no prueban por sí solos 802.11s ni rutas automáticas reales**. No flashar el firmware del proveedor ni experimentar en redes familiares sin permiso.
- Para un prototipo de protección real faltaría implementar cifrado autenticado, protección contra repetición, consentimientos y ensayos de seguridad; CRC32/HTTP local son solo herramientas de laboratorio.
