# GEA LATIDO — Laboratorio reproducible E01 / E02
**Fase II — UVM — 19 noviembre 2026**

## Alcance científico y seguridad
Este repositorio NO proporciona vigilancia, detección de agresiones, cifrado, transmisión por LoRa ni rescate. Solo envía mensajes sintéticos desde Kali o Safari (iPhone) sobre TCP/IP y registra confirmaciones. Ni la red ni el arete se consideran validados. HTTP no está cifrado: usar SOLO con datos inventados, en una LAN privada bajo control, sin NAT/port-forwarding a internet.

### Equipos confirmados
- ZTE ZXHN F670L1FXS (Infinitum): captura del menú `Red local > WLAN > Mesh Wi-Fi`, Mesh Activar apagado, 802.11r apagado. Modelo certificado por Wi-Fi Alliance para Wi-Fi EasyMesh, **no implica 802.11s** ni interoperabilidad con cualquier otro repetidor.
- Steren COM-852: modos router, AP, WISP y repetidor universal documentados. El manual no declara 802.11s ni certificación EasyMesh. Wi-Fi 5 GHz **no equivale a telefonía celular 5G**.
- iPhone 17: Safari transmite carga binaria mediante Wi-Fi local, **sin datos móviles**. iPhone **no es nodo 802.11s** en este experimento.

## 0) Instalar en Kali
El código usa la biblioteca estándar de Python 3: no hay `pip install` para ejecutar el experimento.
```bash
sudo apt update
sudo apt install -y python3 unzip curl iproute2 iw
mkdir -p ~/proyectos/GEA_Latido
cd ~/proyectos/GEA_Latido
# Copiar el ZIP descargado en ~/Descargas y descomprimir:
unzip ~/Descargas/GEA_Latido_Lab_E01_E02.zip
cd GEA_Latido_Lab_E01_E02
python3 -m unittest discover -s tests -v
```
Si el archivo descargado está en `~/Downloads` y no `~/Descargas`, ajusta la ruta. No necesitas conexión a internet para ejecutar el código una vez que lo hayas descargado. La instalación de paquetes `apt` sí requiere repositorios disponibles.

## 1) Prueba E01 en una sola Kali (sin Wi-Fi, sin internet)
Terminal 1:
```bash
cd ~/proyectos/GEA_Latido/GEA_Latido_Lab_E01_E02
python3 server.py --host 127.0.0.1 --port 8080
```
Terminal 2:
```bash
cd ~/proyectos/GEA_Latido/GEA_Latido_Lab_E01_E02
python3 client.py --server http://127.0.0.1:8080 --bits 168,336,672,1344,8192 --n 10 --workers 1 --scenario local --output data/e01_local.csv
```
Archivos: `data/e01_local.csv` (envíos, RTT y fallos) y `data/gea_recepciones.csv` (mensajes efectivamente recibidos). Es una prueba de software en una sola computadora, **no un salto inalámbrico**.

## 2) Prueba E02-A HOT: iPhone 17 a Kali, red online
1. Conecta Kali al Wi-Fi o Ethernet **del ZTE**. Si hay conexión Ethernet, mejor para aislar variaciones.
2. Abre Kali Terminal. Inicia el servidor por red local:
   ```bash
   cd ~/proyectos/GEA_Latido/GEA_Latido_Lab_E01_E02
   python3 server.py --host 0.0.0.0 --port 8080
   ```
3. Segunda Terminal Kali: `ip -br -4 addr`. Identifica la IPv4 de `wlan...` o `enp...`, por ejemplo `192.168.1.64`; ignora `127.0.0.1`, interfaces virtuales y direcciones de Docker/VPN.
4. iPhone: **Configuración → Datos celulares / Red celular → Datos celulares: desactivado**. `Configuración → Wi-Fi` → conectarse al mismo ZTE. Deja Wi-Fi activado. Si iOS muestra *Asistencia para Wi-Fi*, apágala para evitar respaldo de datos celulares.
5. En Safari abre `http://IP_DE_KALI:8080/`. Por ejemplo `http://192.168.1.64:8080/`. No escribir literalmente `IP_DE_KALI`.
6. En escenario selecciona **HOT**. En longitud selecciona **168 bits**. En repeticiones escribe **10**. Pulsa *Enviar mensajes de prueba*. Luego repite con 336, 672, 1344 y 8192 bits.
7. Pulsa *Guardar CSV de tiempos del iPhone* y conserva el archivo. En Kali se genera el CSV de recepciones.
8. Prueba de control: desde Safari abre `http://IP_DE_KALI:8080/health`; debe responder JSON `ok: true`.

## 3) Prueba E02-A COLD: iPhone 17 a Kali sin internet, con Wi-Fi local
La prueba anterior con datos móviles desactivados **NO prueba ausencia total de internet** porque el ZTE aún puede tener internet por fibra.

**Alternativa preferible: usar el Steren como router LAN independiente**, con cable Ethernet desde Kali a uno de sus puertos LAN y **sin cable en WAN**. Antes de modificar su configuración, documenta el estado actual y asegúrate de poder restaurarlo; si el Steren está sirviendo de repetidor a familiares, coordina el horario. 
1. Configura el Steren en **modo Router** con SSID y contraseña nuevos dedicados al laboratorio (el manual lo permite). Deja su puerto WAN **desconectado**, DHCP activo y el dispositivo energizado. No desconectes la fibra PON del ZTE.
2. Conecta Kali por cable Ethernet a un **puerto LAN del Steren**. Alternativa: Kali y iPhone conectados ambos al Wi-Fi del Steren. No uses la red de invitados ni aislamiento de clientes.
3. iPhone: Configuración → Datos celulares: **desactivado**; Configuración → Wi-Fi → selecciona el SSID aislado del Steren. Si iOS dice *Sin conexión a internet*, permanece conectado a esa Wi-Fi.
4. Kali: `ip -br -4 addr` para identificar la nueva dirección LAN. Si Kali conserva otra conexión con salida a internet, desconéctala para esta prueba y registra cómo lo hiciste.
5. `curl -I --max-time 5 https://example.com` en Kali debe fallar por falta de acceso externo; **la falla de DNS por sí sola no basta para caracterizar todo el tráfico**, por eso documenta el WAN desconectado y las conexiones activas. Usa `curl http://IP_DE_KALI:8080/health` para demostrar LAN funcional.
6. Inicia el servidor si no está ejecutándose. Safari abre `http://IP_DE_KALI:8080/`. Selecciona **COLD**, envía 10 paquetes de cada tamaño, guarda CSV y captura pantalla mostrando que el iPhone no tiene internet pero sí llega la alerta.

**Precaución:** la IP del ZTE puede estar en la misma subred que la del Steren (por ejemplo 192.168.1.x). Verifica la interfaz activa y evita que Kali tenga dos enlaces conflictivos a la vez.

## 4) Prueba E02-B: Steren como repetidor del ZTE
**No es mesh multisalto verificada.** Solo estudiar extensión de cobertura y cambios de latencia.
1. No cambiar la configuración si alguien depende del Steren sin consultar antes.
2. Según el manual del COM-852, conéctate a su panel `http://192.168.0.1` o `http://www.wifi.steren.com` (solo si accedes a la red de gestión adecuada).
3. Ve a **Configuración de Internet → Modo de funcionamiento → Repetidor Universal**. Busca SSID del ZTE, selecciónalo y configura la contraseña; aplica y espera el reinicio.
4. Conecta Kali preferiblemente por cable al ZTE o al Wi-Fi principal; el iPhone a la red anunciada por el Steren. Según el manual, los LAN del COM-852 se deshabilitan en el modo repetidor.
5. Confirma que iPhone aún puede abrir `http://IP_DE_KALI:8080/health` y manda cargas en modo **repeater**.
6. Repite a distancias registradas, siempre con autorización y seguridad física, y registra si el repetidor cambió de canal o banda.

## 5) Prueba C — mesh real: NO activar todavía
El ZTE tiene certificación **Wi-Fi EasyMesh** y su configuración incluye `Mesh Activar`. El Steren COM-852 NO está documentado como agente EasyMesh ni nodo 802.11s. La pantalla `802.11r` corresponde a *roaming*, no a mesh multisalto. Para contar saltos se necesitan nodos compatibles y visibilidad de topología/rutas. Con los dos dispositivos actuales no atribuir varios saltos ni cambiar firmware de Infinitum.

En Kali, diagnóstico sin modificar configuraciones:
```bash
./scripts/collect_environment.sh
# Opcional, más detallado:
iw list | sed -n '/Supported interface modes:/,/Band 1:/p' | head -n 40
```
`mesh point` indica soporte del radio Kali para 802.11s pero no asegura que ZTE y Steren entren en la misma malla.

## 6) Comparación controlada, qué recolectar
Medir `RTT` del emisor (milisegundos), entregados/enviados, bits de carga, escenario y lugar anonimizado. Repetir >= 10 veces para diagnóstico; preferentemente >= 100 por condición si hay tiempo. Registrar si online/offline, banda Wi-Fi, distancia, paredes, modo de equipo, potencia y ubicación sin divulgar domicilios exactos. Diferenciar retransmisión en radio de salto IP o salto 802.11s; `traceroute` NO evidencia los saltos de un repetidor capa 2.

## 7) E01 por CLI con concurrencia controlada
En una tercera terminal (Kali en la misma LAN que el servidor):
```bash
python3 client.py --server http://127.0.0.1:8080 --bits 168,336,672,1344,8192 --n 20 --workers 1 --scenario cli --output data/secuencial.csv
python3 client.py --server http://127.0.0.1:8080 --bits 168,336,672,1344,8192 --n 20 --workers 4 --scenario cli --output data/concurrente.csv
```
Aquí `workers=4` prueba **concurrencia de peticiones HTTP**, no caminos de radio simultáneos. Los dos archivos se comparan después; métricas no deben inferirse sin medir. Una comparación rigurosa alternaría el orden de condiciones para reducir sesgos.

## 8) MCP y Kaggle
MCP puede actuar como plano de control para iniciar pruebas, consultar estado y exportar CSV en una computadora local; **no crea conectividad** entre dispositivos ni se necesita para transmitir sin internet. Los ensayos previos en ARC/FAUCON usaron un servidor MCP opcional por `stdio` en Kali, distinto de la prueba GEA. Para E01/E02 basta el servidor HTTP/CLI. La GPU/TPU de Kaggle es remota y requiere internet para enviar trabajos; usaría Kaggle después para simulación grande de grafos, no para transmitir alertas de 21 bytes ni para aumentar el alcance físico. `kaggle kernels push` sirve para ejecutar jobs en Kaggle desde CLI si el entorno tiene conexión y la cuenta tiene recursos disponibles.

## Fuentes y notas
- Certificado Wi-Fi Alliance ZXHN F670L1FXS: https://api.cert.wi-fi.org/api/certificate/download/public?variantId=132077
- Instructivo oficial Steren COM-852: https://descargas.steren.com.mx/COM-852-instr.pdf
- Kaggle CLI: https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md

**Compromiso:** no usar la palabra “cifrado extremo a extremo”, “autenticado” o “mesh validada” con esta implementación; no lo hace. No enviar información de personas reales, audio, ubicación ni contraseñas. El prototipo es una prueba técnica sintética.
