#!/usr/bin/env python3
"""Resume CSV de Safari E03, compara recepciones de B y C por run/seq/bits/hash.
Uso: python3 code/analyze_e03.py --safari ... --b ... --c ... --output ...
"""
import argparse,csv,statistics,math
from collections import defaultdict
from pathlib import Path

def read(path):
    with open(path,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def p95(vals):
    s=sorted(vals)
    if not s:return None
    index=(len(s)-1)*.95; lo=int(index);hi=math.ceil(index)
    return s[lo]+(s[hi]-s[lo])*(index-lo)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--safari',required=True);p.add_argument('--b',required=True);p.add_argument('--c',required=True);p.add_argument('--output',default='data/e03_summary.csv');args=p.parse_args()
    rows=read(args.safari);b=read(args.b);c=read(args.c)
    def key(r):return (r.get('run_id'),str(r.get('sequence',r.get('seq'))),str(r.get('bits')))
    index_b={key(r):r for r in b if r.get('result')=='ok'}
    index_c={key(r):r for r in c if r.get('result')=='ok'}
    groups=defaultdict(list)
    for row in rows:groups[(row['run_id'],row['bits'])].append(row)
    out=[]
    for (rid,bits),records in sorted(groups.items(),key=lambda x:(x[0][0],int(x[0][1]))):
        successful=[r for r in records if str(r.get('ok','')).lower() in ('true','1')]
        ms=[float(r['rtt_ms']) for r in successful if r.get('rtt_ms')]
        matched=0
        for r in successful:
            k=key(r);rb=index_b.get(k);rc=index_c.get(k)
            if rb and rc and rb.get('sha256')==rc.get('sha256')==r.get('sha256') and rb.get('alias_ficticio')==rc.get('alias_ficticio')==r.get('alias_ficticio'):
                matched+=1
        out.append({'run_id':rid,'bits':bits,'sent':len(records),'acked':len(successful),'delivery_pct':round(len(successful)/len(records)*100,2),'matched_B_C':matched,'rtt_mean_ms':round(statistics.mean(ms),3) if ms else '','rtt_median_ms':round(statistics.median(ms),3) if ms else '','rtt_p95_ms':round(p95(ms),3) if ms else '','notes':'B/C match requires identical run_id, seq, bits, sha256, alias'})
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]) if out else ['run_id','bits']);w.writeheader();w.writerows(out)
    for r in out:print(r)
    print('Guardado en',output)
if __name__=='__main__':main()
