# SENTINEL — comandos integrales para Kali, laptop e iPhone

## 0. Antes de operar sin internet

Descargar y extraer el ZIP en Kali y segunda laptop. **Instalar Python 3.10+ con internet antes del aislamiento**. Crear el entorno en la raíz, no uno por experimento:

```bash
cd SENTINEL_E01_E04_GitHub_Reproducible
bash scripts/prepare_offline.sh
bash scripts/run_all_offline.sh
.venv/bin/python scripts/verify_data_integrity.py
```

El `run_all` comprueba código, recalcula observaciones E01/E02 y ejecuta la simulación explícita E04 sin internet. No da por ejecutados experimentos Wi-Fi COLD o RF en campo.

## 1. E01 (Kali, sola computadora)

```bash
bash scripts/e01_loopback.sh
cat runs/e01/cliente.csv
cat runs/e01/gea_recepciones.csv
```

Servidor loopback y cliente en Kali; 5 tamaños × 10 transmisiones, puerto 18080, limpieza automática de proceso.

## 2. E02 HOT (iPhone Wi-Fi, Kali en Ethernet)

```bash
ip -4 -br addr show eth0
sudo ufw status numbered
# Sustituir IP_IPHONE por IP real mostrada en Configuración > Wi-Fi > (i)
sudo ufw allow in on eth0 from IP_IPHONE to any port 8080 proto tcp
.venv/bin/python legacy/e01_e02/server.py \
  --host IP_KALI --port 8080 --data-dir runs/e02_hot
```

En iPhone Safari `http://IP_KALI:8080/` con datos móviles apagados. Ejecutar los seis tamaños disponibles, diez repeticiones por tamaño. Guardar CSV Safari. Para captura en segunda terminal Kali:

```bash
sudo tcpdump -l -ni eth0 'tcp port 8080' | tee runs/e02_hot_tcpdump.txt
```

Detener con Ctrl+C y eliminar exclusivamente la regla creada:

```bash
sudo ufw delete allow in on eth0 from IP_IPHONE to any port 8080 proto tcp
```

## 2b. E02 COLD (Steren sin WAN)

Guardar antes el modo actual del Steren COM-852 y credenciales fuera del repositorio. No reiniciar ZTE. Cambiar Steren a Router LAN+DHCP solo si la configuración previa se puede restaurar. WAN Steren sin cable. iPhone unido al Steren (datos móviles desactivados); Kali cable Ethernet conectado al puerto LAN del Steren. Renovar IP de Kali:

```bash
sudo nmcli device disconnect eth0
sudo nmcli device connect eth0
ip -4 -br addr show eth0
ip -4 route
```

Repetir el montaje HOT con las nuevas IP locales. Comprobar /health del servidor y ausencia de conexión a internet sin datos celulares. Documentar físicamente el puerto WAN vacío. Después cerrar servidor, retirar permiso UFW y regresar el cable de Kali al ZTE y la configuración del Steren al modo original. La guía PDF E02 COLD de 18 páginas se encuentra en `docs/referencias/`.

## 3. E03 (3 equipos físicos, sin internet)

Kali C:

```bash
.venv/bin/python legacy/e03/code/gea_node.py \
  --role sink --node C --host IP_KALI --port 8080 \
  --log runs/e03_C.csv
```

Laptop B (Linux):

```bash
.venv/bin/python legacy/e03/code/gea_node.py \
  --role relay --node B --host IP_LAPTOP --port 8081 \
  --next http://IP_KALI:8080 --log runs/e03_B.csv
```

Laptop B (Windows PowerShell, mismo ZIP y su único venv local):

```powershell
.\.venv\Scripts\python.exe legacy\e03\code\gea_node.py --role relay --node B --host IP_LAPTOP --port 8081 --next http://IP_KALI:8080 --log runs\e03_B.csv
```

iPhone Safari `http://IP_LAPTOP:8081/`; alias LUNA; guardar CSV Safari. Si UFW bloquea en C, permitir solo desde IP_LAPTOP al 8080 con regla temporal. No usar UFW disable ni abrir puertos a internet. La red puede estar aislada WAN, pero un relay HTTP sobre el mismo AP **no equivale** a salto RF.

## 4. E04 simulación offline (sin radios)

```bash
.venv/bin/python -m sentinel.mesh_sim \
  --seed 42 --count 100 --fail-after 50 \
  --output runs/e04_simulacion.csv
```

## 4b. E04 hardware de radios transparentes UART (Linux)

**Antes:** seleccionar hardware compatible, configuración de frecuencia y radio legalmente permitida; instalar y configurar firmware y puertos seriales. E04 con transporte UART documenta paquetes físicos únicamente si se ejecuta en radios reales. Para probar rutas B y D, se desconecta B y se habilita D en una segunda ronda con enlaces RF reales.

C (estación):

```bash
.venv/bin/python -m sentinel.uart_mesh \
 --role sink --node C --device /dev/ttyUSB0 --baud 9600 \
 --radio-model MODELO --firmware VERSION --duration 90 \
 --log runs/e04_C.csv
```

B (relay):

```bash
.venv/bin/python -m sentinel.uart_mesh \
 --role relay --node B --device /dev/ttyUSB0 --baud 9600 \
 --radio-model MODELO --firmware VERSION --duration 90 \
 --log runs/e04_B.csv
```

A (emisor):

```bash
.venv/bin/python -m sentinel.uart_mesh \
 --role source --node A --device /dev/ttyUSB0 --baud 9600 \
 --radio-model MODELO --firmware VERSION --n 10 \
 --interval 2 --duration 40 --log runs/e04_A.csv
```

En terminal C, el operador escribe `atender 1` para confirmar **solo su lectura simulada** de la alerta 1. Combinar los CSV:

```bash
.venv/bin/python scripts/merge_rf_logs.py \
 runs/e04_A.csv runs/e04_B.csv runs/e04_C.csv \
 --out runs/e04_rf_consolidado.csv
.venv/bin/python -m sentinel.verify_rf runs/e04_rf_consolidado.csv
```

Las radios transparentes UART no hacen autoenrutamiento por este código. El laboratorio debe medir enlace directo A–C y demostrar que el paquete llega C mediante B; el archivo consolidado debe mostrar recepción por dos saltos con la misma secuencia y hash. E04 no llama a emergencia real.

## 5. GitHub

`git init && git add . && git commit -m "SENTINEL E01-E04 reproducible"` funciona offline. Al recuperar internet y crear un repositorio vacío en GitHub, usar `git remote add origin https://github.com/USUARIO/REPO.git && git push -u origin main`. Documentar sistema operativo, versión Python y firmware de radio de los nuevos ensayos antes del commit.
