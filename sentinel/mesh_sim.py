"""E04: simulador discreto reproducible de rutas; NO constituye radio Sub-GHz medido."""
from __future__ import annotations
import argparse,csv,json,random,statistics,hashlib,time
from pathlib import Path

# Cada enlace representa un salto RF hipotético. Tiempos y pérdidas sintéticos.
LINKS={('A','B'):(20.,.018),('B','C'):(18.,.026),('A','D'):(34.,.018),('D','C'):(24.,.022)}
ROUTES=[('A','B','C'),('A','D','C')]
COLUMNS=['run_id','provenance','sequence','node','state','route','hop','elapsed_ms','payload_hash','detail']

def choose_route(disabled):
    for route in ROUTES:
        if not set(route)&disabled:return route
    return None

def simulate(seed=42,count=100,fail_after=50,attend=True,output=None):
    rng=random.Random(seed); rows=[];delivered=[];elapsed=[];last_route=None
    run_id=f'SIM-E04-s{seed}-n{count}'
    def write(seq,node,state,route,hop,t,payload_hash,detail=''):
        rows.append(dict(run_id=run_id,provenance='SIMULADO_NO_RF',sequence=seq,node=node,state=state,route='>'.join(route or []),hop=hop,elapsed_ms=f'{t:.3f}',payload_hash=payload_hash,detail=detail))
    for seq in range(1,count+1):
        disabled={'B'} if seq>fail_after else set()
        route=choose_route(disabled)
        frame=b'\x01SOS-LUNA-'+seq.to_bytes(4,'big')
        digest=hashlib.sha256(frame).hexdigest();now=0.0
        write(seq,'A','GENERADO',route,0,now,digest)
        if route is None:
            write(seq,'A','SIN_RUTA',route,0,now,digest,'No hay ruta alternativa');delivered.append(False);continue
        last_route=route
        ok=True
        for hop,(sender,receiver) in enumerate(zip(route,route[1:]),1):
            latency,loss=LINKS[(sender,receiver)]
            now+=max(1.,rng.gauss(latency,latency*.17))
            if rng.random()<loss:
                write(seq,sender,'PERDIDO_EN_ENLACE',route,hop,now,digest,f'{sender}->{receiver}')
                ok=False;break
            write(seq,receiver,'RECIBIDO' if hop==1 else 'TRANSITO',route,hop,now,digest,f'ACK {sender}->{receiver}')
        if ok:
            write(seq,route[-1],'ENTREGADO',route,len(route)-1,now,digest,'ACK de estacion')
            if attend:write(seq,'OPERADOR_PRUEBA','ATENDIDO_SIMULADO',route,len(route)-1,now+5.0,digest,'Confirmacion manual simulada')
            elapsed.append(now)
        delivered.append(ok)
    summary={'provenance':'SIMULADO_NO_RF','seed':seed,'total':count,'delivered':sum(delivered), 'pdr_pct':round(100*sum(delivered)/count,3),'p50_ms':round(statistics.median(elapsed),3) if elapsed else None,'after_failure':sum(delivered[fail_after:]),'after_failure_attempts':len(delivered[fail_after:]),'routes':['A>B>C','A>D>C'],'note':'Las perdidas/latencias son sintéticas; no representan PDR real de LoRa'}
    if output:
        out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=COLUMNS);w.writeheader();w.writerows(rows)
        out.with_suffix('.summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return rows,summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--count',type=int,default=100)
    p.add_argument('--fail-after',type=int,default=50)
    p.add_argument('--output',default='runs/e04_simulacion.csv')
    a=p.parse_args()
    if a.count<1 or a.fail_after<0: p.error('count debe ser positivo y fail-after >=0')
    rows,s=simulate(a.seed,a.count,a.fail_after,output=a.output)
    print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
