#!/usr/bin/env python3
"""Genera diagramas y gráficas vectoriales SVG solamente con biblioteca estándar."""
from pathlib import Path
from math import log10
from statistics import median
import csv,html
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sentinel.analyze import parse,percentile
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
RED='#B51B33';DARK='#212733';G='#636B75';L='#E4E7EA';WHITE='#FFFFFF';ROSE='#FAECEF';GREEN='#268069'

def svg_start(w=1200,h=360):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="white"/>']
def rect(a,x,y,w,h,fill=WHITE,stroke=L,r=12):a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
def txt(a,x,y,t,size=21,color=DARK,weight=400,anchor='middle'):
 a.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(str(t))}</text>')
def arrow(a,x1,y1,x2,y2,label=None,red=True):
 c=RED if red else G
 a.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/>')
 a.append(f'<polygon points="{x2},{y2} {x2-14},{y2-8} {x2-14},{y2+8}" fill="{c}"/>')
 if label:txt(a,(x1+x2)/2,(y1+y2)/2-18,label,17,c,500)
def save(file,a): (OUT/file).write_text(''.join(a+['</svg>']),encoding='utf-8')
def box(a,x,y,w,h,title,lines,accent=False):
 rect(a,x,y,w,h,ROSE if accent else '#F7F8FA',RED if accent else L)
 txt(a,x+w/2,y+49,title,26,RED,700)
 for i,line in enumerate(lines):txt(a,x+w/2,y+88+i*30,line,19,DARK)

# E01
s=svg_start(1200,370);txt(s,600,45,'E01  •  Banco loopback (127.0.0.1)',29,RED,700)
box(s,92,96,410,173,'Cliente Python',['168 / 336 / 672 / 1344 / 8192 bits','10 repeticiones por tamaño'],True)
box(s,698,96,410,173,'Servidor Kali',['HTTP POST → ACK y SHA-256','CSV + prueba unitaria'])
arrow(s,518,166,674,166,'POST');arrow(s,674,214,518,214,'ACK',False)
txt(s,600,320,'Mismo equipo físico: latencia local, no salto RF',19,G);save('E01_loopback.svg',s)

s=svg_start(1200,400);txt(s,600,44,'E02  •  HOT frente a COLD',29,RED,700)
box(s,78,92,290,160,'iPhone Safari',['Mensaje sintético','Wi-Fi local'],True)
box(s,462,92,278,160,'Router/AP',['HOT: ZTE con WAN','COLD: Steren sin WAN'])
box(s,828,92,290,160,'Kali Ethernet',['HTTP :8080','ACK + CSV'])
arrow(s,376,165,448,165);arrow(s,748,165,813,165)
txt(s,600,306,'HOT: internet disponible en router. COLD: aislamiento físico WAN verificado.',18,DARK)
txt(s,600,338,'Seleccionar COLD en Safari no demuestra desconexión de internet.',17,RED,600)
save('E02_hot_cold.svg',s)

s=svg_start(1200,390);txt(s,600,44,'E03  •  Mini-servidores de aplicación',29,RED,700)
for x,w,t,lines in [(55,290,'A • iPhone',['Navegador / LUNA','Emisor Wi-Fi']),(456,290,'B • Laptop',['Relay HTTP 8081','ACK y bitácora']),(859,290,'C • Kali',['Sink HTTP 8080','Hash y CSV'])]:box(s,x,100,w,171,t,lines,x==55)
arrow(s,352,180,443,180);arrow(s,752,180,847,180)
txt(s,600,324,'Relay en máquina diferente = retransmisión de aplicación; no implica 2 saltos de radio.',17,G)
save('E03_relay.svg',s)

s=svg_start(1200,450);txt(s,600,44,'E04  •  Hipótesis RF multihop: ruta primaria y alternativa',26,RED,700)
coords={'A':(120,225),'B':(460,125),'D':(460,325),'C':(835,225)}
for u,v,label in [('A','B','ruta 1'),('B','C','ruta 1'),('A','D','ruta 2'),('D','C','ruta 2')]:
 x,y=coords[u];x2,y2=coords[v]
 s.append(f'<path d="M{x+64} {y} L{x2-70} {y2}" stroke="{RED if v=="B" or u=="B" else GREEN}" stroke-width="5" fill="none" stroke-dasharray="{ "0" if v=="B" or u=="B" else "9 7"}"/>')
for name,(x,y) in coords.items():
 s.append(f'<circle cx="{x}" cy="{y}" r="55" fill="{DARK if name=="C" else RED}"/>');txt(s,x,y+10,name,32,WHITE,700)
box(s,960,151,190,160,'Estación',['Recepción SOS','ACK final'],False)
arrow(s,890,225,947,225)
txt(s,600,410,'A–B–C y A–D–C: rutas conceptuales. Validación requiere radios, firmware y registros independientes.',15,G)
save('E04_mesh_topologia.svg',s)

s=svg_start(1200,310);txt(s,600,44,'E04  •  Cuatro estados auditables del SOS',29,RED,700)
stages=[('1  GENERADO','Emisor A'),('2  RECIBIDO','Primer nodo'),('3  ENTREGADO','Estación'),('4  ATENDIDO','Operador de prueba')]
for i,(t,b) in enumerate(stages):
 x=26+i*297;box(s,x,103,261,123,t,[b],i==0)
 if i<3:arrow(s,x+263,167,x+291,167)
txt(s,600,270,'Atendido significa confirmación manual simulada; no intervención ni rescate.',17,G)
save('E04_cuatro_estados.svg',s)

# charts
E1=parse(ROOT/'data/observados/e01_loopback_50.csv','e01');E2=parse(ROOT/'data/observados/e02_hot_50_conciliados.csv','e02')
s=svg_start(1200,450);txt(s,600,42,'E01 vs E02 HOT  •  latencia RTT real (n=50 por ensayo)',27,RED,700)
for yy,t in [(105,0),(160,15),(215,30),(270,45),(325,60)]:
 # grid x representing RTT 0..60
 x=126+int(t/60*970);s.append(f'<path d="M{x} 82 L{x} 330" stroke="{L}" stroke-width="1"/>');txt(s,x,356,str(t),16,G)
txt(s,600,387,'Tiempo RTT (ms); escala truncada a 60 ms. Valor extremo E02: 211 ms (conservado en CSV).',17,G)
for i,(name,d) in enumerate([('E01 loopback',E1),('E02 HOT',E2)]):
 y=150+i*100;vals=[r['rtt_ms'] for r in d];p50=percentile(vals,50);p95=percentile(vals,95)
 s.append(f'<path d="M126 {y} L{126+min(p95,60)/60*970} {y}" stroke="{GREEN}" stroke-width="13" stroke-linecap="round"/>')
 s.append(f'<circle cx="{126+min(p50,60)/60*970}" cy="{y}" r="10" fill="{RED}"/>')
 txt(s,106,y-24,name,20,DARK,700,'start');txt(s,1035,y-24,f'p50={p50:.1f} / p95={p95:.1f} ms',16,RED,600)
save('E01_E02_RTT_reales.svg',s)

s=svg_start(1200,440);txt(s,600,43,'E04  •  Matriz propuesta: entrega frente a distancia',28,RED,700)
X=[0,100,250,500,1000];x0=145
for i,v in enumerate(X):
 x=x0+i*210;txt(s,x,346,f'{v} m',17,DARK,500);s.append(f'<path d="M{x} 100 L{x} 325" stroke="{L}" stroke-width="1"/>')
for v in [0,25,50,75,95,100]:
 y=322-v*2.2;s.append(f'<path d="M145 {y} L985 {y}" stroke="{RED if v==95 else L}" stroke-width="{3 if v==95 else 1}" stroke-dasharray="{ "7 6" if v==95 else "2 3"}"/>');txt(s,111,y+5,f'{v} %',16,G)
txt(s,750,110,'META ≥95 %',20,RED,700)
txt(s,590,387,'Sin puntos RF observados: cada distancia exige n, entrega, LOS/NLOS, RSSI/SNR e IC95 %.',17,G)
save('E04_PDR_distancia_plan.svg',s)

s=svg_start(1200,455);txt(s,600,43,'915 MHz  •  Pérdida ideal en espacio libre (FSPL)',28,RED,700)
D=[1,2.5,5,15];v=[32.44+20*log10(x)+20*log10(915) for x in D]
for idx,(x,yv) in enumerate(zip(D,v)):
 xpix=170+idx*285;y=335-(yv-80)*5.2
 s.append(f'<rect x="{xpix-55}" y="{y}" width="110" height="{335-y}" rx="8" fill="{RED}"/>')
 txt(s,xpix,y-16,f'{yv:.1f} dB',23,DARK,700);txt(s,xpix,371,f'{x:g} km',19,DARK)
txt(s,600,420,'Cálculo teórico LOS; no demuestra alcance real. Margen requiere potencia, ganancias y sensibilidad.',17,G)
save('E04_FSPL_915MHz.svg',s)
print('Figuras SVG:',len(list(OUT.glob('*.svg'))))
