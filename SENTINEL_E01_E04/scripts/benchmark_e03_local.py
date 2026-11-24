#!/usr/bin/env python3
"""Repetición instrumentada E03 en procesos localhost: HTTP, no radio RF."""
from __future__ import annotations
import csv,hashlib,json,os,socket,statistics,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from urllib import request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'legacy/e03/code'))
from send_probe import payload
from sentinel.analyze import percentile,wilson95
SIZES=(168,336,672,1344,8192,32768)

def freeport():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));return sock.getsockname()[1]

def wait(port):
    for _ in range(75):
        try:
            with request.urlopen(f'http://127.0.0.1:{port}/health',timeout=0.2) as resp:
                if resp.status==200:return
        except Exception:time.sleep(0.06)
    raise RuntimeError(f'No inició puerto {port}')

def run(outdir='runs/e03_repeticion'):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    ports={name:freeport() for name in ('C','B1','B2')};proc=[];rows=[]
    config=[('C','sink',None),('B1','relay','C'),('B2','relay','B1')]
    try:
        for name,role,nextnode in config:
            args=[sys.executable,str(ROOT/'legacy/e03/code/gea_node.py'),'--role',role,'--node',name,
              '--host','127.0.0.1','--port',str(ports[name]),'--log',str(outdir/f'nodo_{name}.csv')]
            if nextnode:args+=['--next',f'http://127.0.0.1:{ports[nextnode]}']
            proc.append(subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT))
            wait(ports[name])
        for route,origin in [('directa','C'),('dos_relays','B2')]:
            for bits in SIZES:
                for j in range(10):
                    seq=1+SIZES.index(bits)*10+j+(0 if route=='directa' else 60)
                    frame=payload(bits,'LUNA',seq);t0=time.perf_counter_ns()
                    ok=False;error='';ack={}
                    try:
                        req=request.Request(f'http://127.0.0.1:{ports[origin]}/api/alert',data=frame,
                           headers={'Content-Type':'application/octet-stream','X-GEA-Run-ID':'E03_REPRO_2026'},method='POST')
                        with request.urlopen(req,timeout=4) as response:ack=json.load(response)
                        ok=bool(ack.get('ok') and ack.get('sha256')==hashlib.sha256(frame).hexdigest() and
                          ack.get('sequence')==seq and ack.get('bits')==bits)
                    except Exception as exc:error=f'{type(exc).__name__}:{exc}'
                    elapsed=round((time.perf_counter_ns()-t0)/1e6,4)
                    rows.append({'procedencia':'MEDIDO_HTTP_LOCALHOST_REPETICION','ruta':route,'seq':seq,'bits':bits,
                      'confirmado':int(ok),'rtt_ms':elapsed,'ruta_de_ack':'>'.join(ack.get('route',[])),
                      'hash_sha256':ack.get('sha256',''),'error':error})
        with (outdir/'envios_120.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
        stats={}
        for route in ('directa','dos_relays'):
            ar=[r for r in rows if r['ruta']==route];ok=[r['rtt_ms'] for r in ar if r['confirmado']]
            stats[route]={'procedencia':'MEDIDO_HTTP_LOCALHOST_REPETICION','n':len(ar),'confirmados':len(ok),
               'pdr_pct':round(100*len(ok)/len(ar),2),'p50_ms':round(percentile(ok,50),3),
               'p95_ms':round(percentile(ok,95),3),'ic95_wilson_pct':wilson95(len(ok),len(ar))}
        (outdir/'resumen.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(stats,ensure_ascii=False,indent=2));return stats
    finally:
        for item in proc:item.terminate()
        for item in proc:
            try:item.wait(timeout=2)
            except subprocess.TimeoutExpired:item.kill()

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',default='runs/e03_repeticion')
    args=ap.parse_args();run(args.output_dir)
