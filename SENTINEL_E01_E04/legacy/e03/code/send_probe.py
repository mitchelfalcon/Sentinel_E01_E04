#!/usr/bin/env python3
"""Emisor opcional de escritorio para comprobar E03 sin iPhone, estandar Python."""
import argparse,csv,hashlib,json,struct,time,zlib
from pathlib import Path
from urllib import request

def payload(bits,alias,seq):
    alias=alias.upper()
    assert 1<=len(alias)<=6 and alias.isascii() and alias.isalnum()
    a=bytearray(bits//8);a[0:2]=b'\x02\x03';a[2:2+len(alias)]=alias.encode('ascii')
    struct.pack_into('!II',a,8,seq,int(time.time()))
    for j in range(17,len(a)-4):a[j]=(j*7+seq)%251
    struct.pack_into('!I',a,len(a)-4,zlib.crc32(a[:-4])&0xffffffff)
    return bytes(a)

def main():
    p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--alias',default='LUNA');p.add_argument('--bits',default='168,336,672,1344,8192,32768');p.add_argument('--n',type=int,default=10);p.add_argument('--run',default='E03_PROBE');p.add_argument('--csv',default='data/e03_probe.csv');a=p.parse_args()
    out=Path(a.csv);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['utc','run_id','alias_ficticio','seq','bits','ok','rtt_ms','route','sha256','error']);w.writeheader()
        n=0
        for bits in [int(x) for x in a.bits.split(',')]:
            for _ in range(a.n):
                n+=1;blob=payload(bits,a.alias,n);start=time.perf_counter();ok=False;err='';route='';dig=''
                try:
                    req=request.Request(a.url.rstrip('/')+'/api/alert',data=blob,method='POST',headers={'Content-Type':'application/octet-stream','X-GEA-Run-ID':a.run,'X-GEA-TTL':'6'})
                    with request.urlopen(req,timeout=10) as rsp:ack=json.load(rsp)
                    ok=ack.get('ok') and ack.get('sequence')==n and ack.get('sha256')==hashlib.sha256(blob).hexdigest() and ack.get('alias_ficticio')==a.alias.upper()
                    route='>'.join(ack.get('route',[]));dig=ack.get('sha256','')
                except Exception as ex:err=str(ex)
                w.writerow({'utc':time.strftime('%Y-%m-%dT%H:%M:%S'),'run_id':a.run,'alias_ficticio':a.alias.upper(),'seq':n,'bits':bits,'ok':bool(ok),'rtt_ms':round((time.perf_counter()-start)*1000,2),'route':route,'sha256':dig,'error':err})
                print(bits,n,'OK' if ok else 'FALLO',route,err)
    print('Archivo:',out)
if __name__=='__main__':main()
