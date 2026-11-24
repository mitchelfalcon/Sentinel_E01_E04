#!/usr/bin/env python3
"""Smoke test completamente offline, relays en localhost (NO prueba RF)."""
import csv,json,socket,subprocess,sys,tempfile,time
from pathlib import Path
from urllib import request,error
from send_probe import payload
from hashlib import sha256
BASE=Path(__file__).resolve().parent

def port():
    s=socket.socket();s.bind(('127.0.0.1',0));n=s.getsockname()[1];s.close();return n

def wait(p):
    for _ in range(50):
        try:
            with request.urlopen(f'http://127.0.0.1:{p}/health',timeout=.2) as r:
                if r.status==200:return
        except Exception:time.sleep(.07)
    raise AssertionError('Servidor no arrancó')

def run():
    ports=[port(),port(),port()];procs=[]
    with tempfile.TemporaryDirectory() as d:
        try:
            for i in (2,1,0):
                args=[sys.executable,str(BASE/'gea_node.py'),'--role','sink' if i==2 else 'relay','--node','BCD'[i],'--host','127.0.0.1','--port',str(ports[i]),'--log',str(Path(d)/f'{i}.csv')]
                if i<2:args += ['--next',f'http://127.0.0.1:{ports[i+1]}']
                procs.append(subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT));wait(ports[i])
            for i,bits in enumerate((168,336,672,1344,8192,32768),1):
                raw=payload(bits,'LUNA',i)
                req=request.Request(f'http://127.0.0.1:{ports[0]}/api/alert',data=raw,headers={'X-GEA-Run-ID':'PRUEBA','Content-Type':'application/octet-stream'},method='POST')
                with request.urlopen(req,timeout=5) as r:ack=json.load(r)
                assert ack['ok'] and ack['route']==['B','C','D'] and ack['alias_ficticio']=='LUNA' and ack['bits']==bits and ack['sha256']==sha256(raw).hexdigest()
            broken=bytearray(payload(168,'LUNA',77));broken[2]^=1
            req=request.Request(f'http://127.0.0.1:{ports[0]}/api/alert',data=bytes(broken),method='POST')
            try:request.urlopen(req,timeout=3)
            except error.HTTPError as e:assert e.code==400;e.close()
            else:raise AssertionError('Fallo de detección de corrupción CRC')
            for i in (0,1,2):
                with open(Path(d)/f'{i}.csv',newline='') as f:rows=list(csv.DictReader(f))
                assert len([r for r in rows if r['result']=='ok'])==6
            print('OK E03v2: 6 longitudes, alias LUNA en 21 bytes, 2 relays logicos, SHA256 igual, CRC32 corrupcion rechazada. 0 saltos RF probados.')
        finally:
            for p in procs:p.terminate()
            for p in procs:
                try:p.wait(timeout=3)
                except subprocess.TimeoutExpired:p.kill()
if __name__=='__main__':run()
