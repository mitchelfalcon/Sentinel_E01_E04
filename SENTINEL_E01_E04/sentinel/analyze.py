"""Análisis reproducible de registros observados E01 y E02. Sin dependencias."""
import csv,json,statistics,math,argparse
from pathlib import Path

def percentile(v,p):
    if not v:return None
    a=sorted(v);x=(len(a)-1)*p/100.0;i=int(x);f=x-i
    return a[i]*(1-f)+a[min(i+1,len(a)-1)]*f

def parse(path,kind):
    with Path(path).open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if kind=='e01': return [{'bits':int(r['bits']),'ok':r['result'].lower()=='ok','rtt_ms':float(r['rtt_ms'])} for r in rows]
    if kind=='e02': return [{'bits':int(r['payload_bits']),'ok':r['iphone_ack'].lower()=='true' and bool(r['received_kali_utc']),'rtt_ms':float(r['iphone_rtt_ms'])} for r in rows]
    raise ValueError(kind)

def wilson95(success,total):
    """Intervalo Wilson binomial 95 %, z=1.959963984540054."""
    if total<=0:return (None,None)
    z=1.959963984540054;p=success/total;den=1+z*z/total
    cen=(p+z*z/(2*total))/den
    h=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return (round(100*max(0,cen-h),2),round(100*min(1,cen+h),2))

def stats(rows):
    rr=[r['rtt_ms'] for r in rows if r['ok']]
    return dict(n=len(rows),ack=sum(x['ok'] for x in rows),pdr_pct=round(100*sum(x['ok'] for x in rows)/len(rows),3) if rows else None,p50_ms=round(percentile(rr,50),3) if rr else None,p95_ms=round(percentile(rr,95),3) if rr else None,mean_ms=round(statistics.mean(rr),3) if rr else None,max_ms=max(rr) if rr else None,wilson95_pct=wilson95(sum(x['ok'] for x in rows),len(rows)))

def analyze(folder='data/observados',out='runs/estadisticas_observadas.json'):
    d=Path(folder);a=parse(d/'e01_loopback_50.csv','e01');b=parse(d/'e02_hot_50_conciliados.csv','e02')
    result={'method':'percentil interpolado de posiciones (n-1)*p/100','e01':stats(a),'e02_hot':stats(b),'by_bits':{},'notes':['E01 es loopback en Kali. E02 es RTT HTTP Safari - Kali sobre LAN HOT. No se midió Sub-GHz.','Los 180 registros de Safari incluyen etiquetas de escenario, no prueban aislamiento WAN.','Los intervalos de confianza deben considerar el tamaño de muestra y método de selección.']}
    for label,data in [('e01',a),('e02_hot',b)]:
        result['by_bits'][label]={str(bits):stats([r for r in data if r['bits']==bits]) for bits in sorted(set(x['bits'] for x in data))}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/observados');p.add_argument('--out',default='runs/estadisticas_observadas.json');a=p.parse_args()
    print(json.dumps(analyze(a.data,a.out),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
