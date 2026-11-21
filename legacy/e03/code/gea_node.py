#!/usr/bin/env python3
"""GEA E03 v2 — experimentacion de transporte offline. NO es un sistema de emergencias.
Python 3.10+ y solo biblioteca estandar. No cifrado ni autenticacion.
"""
import argparse, csv, hashlib, json, re, struct, threading, time, zlib
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import request, error

SIZES = {21, 42, 84, 168, 1024, 4096}
COLUMNS = ['utc','node','role','run_id','alias_ficticio','sequence','bits','sha256','crc32_ok','result','route','ttl_in','processing_ms','peer']
LOCK = threading.Lock()

HTML = r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GEA Latido E03 v2 offline</title><style>body{font:16px system-ui,sans-serif;background:#f5f0f8;color:#2f1d3b;padding:14px}main{max-width:560px;margin:0 auto;background:white;padding:22px;border-radius:20px;border:1px solid #dec9eb}h1{color:#532a74}label{display:block;margin:14px 0 5px;font-weight:600}input,button,select{width:100%;box-sizing:border-box;padding:12px;border-radius:9px;border:1px solid #bda6cb;font:inherit}button{background:#67368d;color:white;font-weight:700;margin-top:16px}pre{font:12px ui-monospace,monospace;background:#221c2e;color:#f2e8f6;padding:12px;white-space:pre-wrap;overflow:auto;max-height:250px;border-radius:12px}.note{font-size:13px;color:#63526c}</style></head><body><main>
<div class="note">UVM · E03 · LAN aislada · Solo ensayo</div><h1>GEA Latido | Mini-servidores</h1><p>Envia datos reales por Wi-Fi/LAN sin internet. Un alias ficticio forma parte de los 21 bytes minimos.</p>
<label>Nombre ficticio (1 a 6 letras o numeros)</label><input id="alias" value="LUNA" maxlength="6" pattern="[A-Za-z0-9]{1,6}">
<label>Carga binaria</label><select id="bits"><option value="168">168 bits / 21 bytes</option><option value="336">336 bits / 42 bytes</option><option value="672">672 bits / 84 bytes</option><option value="1344">1344 bits / 168 bytes</option><option value="8192">8192 bits / 1024 bytes</option><option value="32768">32768 bits / 4096 bytes</option></select>
<label>Intentos</label><input id="count" type="number" min="1" max="100" value="10">
<label>ID de ensayo</label><input id="runid" value="E03_FIS1_OFFLINE">
<button id="send" onclick="send()">Enviar a traves de B y C</button><button onclick="download()" style="background:#8e739a">Guardar CSV Safari</button>
<p id="summary">Esperando envios...</p><pre id="log">Sin actividad</pre><p class="note">CRC32 detecta errores accidentales, no proporciona seguridad criptografica. Sin grabacion ni datos personales. La red HTTP carece de cifrado.</p>
<script>
let seq=1,records=[];function crc32(u){let c=0xffffffff;for(let i=0;i<u.length;i++){c^=u[i];for(let k=0;k<8;k++)c=(c>>>1)^((c&1)?0xEDB88320:0)}return(c^0xffffffff)>>>0}
function makePacket(bits,alias,number){let a=new Uint8Array(bits/8),d=new DataView(a.buffer);a[0]=2;a[1]=3;for(let i=0;i<alias.length;i++)a[2+i]=alias.charCodeAt(i);d.setUint32(8,number,false);d.setUint32(12,Math.floor(Date.now()/1000)>>>0,false);a[16]=0;for(let i=17;i<a.length-4;i++)a[i]=(i*7+number)%251;d.setUint32(a.length-4,crc32(a.subarray(0,a.length-4)),false);return a}
async function send(){const name=document.getElementById('alias').value.trim().toUpperCase();if(!/^[A-Z0-9]{1,6}$/.test(name)){alert('Introduce 1 a 6 letras/numeros ASCII, por ejemplo LUNA');return}const bits=Number(document.getElementById('bits').value),count=Math.max(1,Math.min(100,Number(document.getElementById('count').value)||1)),id=document.getElementById('runid').value.replace(/[^A-Za-z0-9_-]/g,'_').slice(0,40)||'E03';const btn=document.getElementById('send');btn.disabled=true;for(let j=0;j<count;j++){let n=seq++,t=performance.now(),ok=false,route='',sha='',err='';try{let c=new AbortController(),timer=setTimeout(()=>c.abort(),10000);try{let resp=await fetch('/api/alert',{method:'POST',body:makePacket(bits,name,n),headers:{'Content-Type':'application/octet-stream','X-GEA-Run-ID':id,'X-GEA-TTL':'6'},signal:c.signal,cache:'no-store'}),ack=await resp.json();ok=!!(resp.ok&&ack.ok&&ack.sequence===n&&ack.bits===bits&&ack.alias_ficticio===name);route=(ack.route||[]).join('>');sha=ack.sha256||'';if(!ok)err=ack.error||'ACK no coincide'}finally{clearTimeout(timer)}}catch(e){err=String(e.message||e)}let ms=+(performance.now()-t).toFixed(2);records.push({utc:new Date().toISOString(),run_id:id,alias_ficticio:name,sequence:n,bits,ok,rtt_ms:ms,route,sha256:sha,error:err});document.getElementById('log').textContent=(ok?'OK ':'FALLO ')+name+' seq='+n+' bits='+bits+' RTT='+ms+'ms ruta='+route+' '+err+'\n'+document.getElementById('log').textContent;let g=records.filter(r=>r.run_id===id);document.getElementById('summary').textContent='Intentos: '+g.length+' · Confirmados: '+g.filter(r=>r.ok).length+' · Ultima ruta: '+route}btn.disabled=false}
function download(){const keys=['utc','run_id','alias_ficticio','sequence','bits','ok','rtt_ms','route','sha256','error'];const lines=[keys.join(','),...records.map(r=>keys.map(k=>'"'+String(r[k]??'').replaceAll('"','""')+'"').join(','))];let u=URL.createObjectURL(new Blob(['\ufeff'+lines.join('\n')],{type:'text/csv'})),a=document.createElement('a');a.href=u;a.download='GEA_E03_iPhone_alias.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),3000)}
</script></main></body></html>'''


def decode(raw):
    if len(raw) not in SIZES or raw[0:2] != b'\x02\x03':
        raise ValueError('Longitud/version/tipo invalido')
    alias_bytes = raw[2:8].rstrip(b'\x00')
    try: alias = alias_bytes.decode('ascii')
    except UnicodeDecodeError: raise ValueError('Alias no ASCII')
    if not re.fullmatch(r'[A-Z0-9]{1,6}', alias): raise ValueError('Alias no valido')
    seq, stamp = struct.unpack_from('!II',raw,8)
    expected = struct.unpack_from('!I',raw,len(raw)-4)[0]
    actual = zlib.crc32(raw[:-4]) & 0xffffffff
    if expected != actual: raise ValueError('CRC32 no coincide')
    return dict(alias_ficticio=alias, sequence=seq, timestamp_utc=stamp,bits=len(raw)*8,sha256=hashlib.sha256(raw).hexdigest())


def factory(config):
    path=Path(config.log);path.parent.mkdir(parents=True,exist_ok=True)
    def write_log(entry):
        with LOCK:
            fresh = not path.exists() or path.stat().st_size==0
            with path.open('a',newline='',encoding='utf-8') as f:
                writer=csv.DictWriter(f,fieldnames=COLUMNS)
                if fresh:writer.writeheader()
                writer.writerow(entry)
    class Handler(BaseHTTPRequestHandler):
        server_version='GEA-E03-Offline/2.0'
        def log_message(self,fmt,*args):print('[%s] %s'%(config.node,fmt%args),flush=True)
        def respond(self,status,obj):
            payload=json.dumps(obj,ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(payload)))
            self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(payload)
        def do_GET(self):
            if self.path=='/health':return self.respond(200,{'ok':True,'node':config.node,'role':config.role,'next':config.next})
            if self.path!='/':return self.respond(404,{'ok':False,'error':'No encontrado'})
            payload=HTML.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length',str(len(payload)))
            self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(payload)
        def do_POST(self):
            if self.path!='/api/alert':return self.respond(404,{'ok':False,'error':'No encontrado'})
            started=time.monotonic(); p={'alias_ficticio':'','sequence':-1,'bits':0,'sha256':''};ttl=0;rid='E03';result='';route=[]
            try:
                n=int(self.headers.get('Content-Length','-1'))
                if n not in SIZES:raise ValueError('Tamano fuera del protocolo')
                raw=self.rfile.read(n)
                if len(raw)!=n:raise ValueError('Datos incompletos')
                p=decode(raw)
                rid=re.sub(r'[^A-Za-z0-9_-]','_',self.headers.get('X-GEA-Run-ID','E03'))[:40] or 'E03'
                ttl=int(self.headers.get('X-GEA-TTL','6'))
                if not 1<=ttl<=10:raise ValueError('TTL fuera de limites')
                previous=[x for x in self.headers.get('X-GEA-Route','').split(',') if x]
                if config.node in previous or len(previous)>9:raise ValueError('Ciclo o ruta larga')
                route=previous+[config.node]
                ack=dict(ok=True,sequence=p['sequence'],bits=p['bits'],alias_ficticio=p['alias_ficticio'],sha256=p['sha256'],route=route,relays=len(route)-1,run_id=rid)
                if config.role=='relay':
                    if ttl<=1:raise ValueError('TTL agotado')
                    req=request.Request(config.next.rstrip('/')+'/api/alert',data=raw,method='POST',headers={'Content-Type':'application/octet-stream','X-GEA-Run-ID':rid,'X-GEA-TTL':str(ttl-1),'X-GEA-Route':','.join(route)})
                    try:
                        with request.urlopen(req,timeout=config.timeout) as resp:
                            if resp.status!=200:raise RuntimeError('HTTP destino no es 200')
                            ack=json.loads(resp.read(16000))
                    except (error.URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:raise RuntimeError('Fallo del siguiente nodo: '+str(exc)) from exc
                    if not(ack.get('ok') and ack.get('sha256')==p['sha256'] and ack.get('sequence')==p['sequence'] and ack.get('alias_ficticio')==p['alias_ficticio'] and ack.get('bits')==p['bits']):raise RuntimeError('Confirmacion destino no coincide')
                    route=ack['route']
                result='ok'
                print(f'[{config.node}] RECIBIDO alias={p["alias_ficticio"]} seq={p["sequence"]} bits={p["bits"]} ruta={">".join(route)}',flush=True)
                return self.respond(200,ack)
            except (ValueError,RuntimeError,TypeError) as exc:
                result='error: '+str(exc)[:100]
                print(f'[{config.node}] RECHAZADO: {result}',flush=True)
                return self.respond(400 if isinstance(exc,ValueError) else 502,{'ok':False,'error':str(exc)[:180]})
            finally:
                write_log({'utc':datetime.now(timezone.utc).isoformat(),'node':config.node,'role':config.role,'run_id':rid,'alias_ficticio':p['alias_ficticio'],'sequence':p['sequence'],'bits':p['bits'],'sha256':p['sha256'],'crc32_ok':bool(p['sha256']),'result':result,'route':'>'.join(route),'ttl_in':ttl,'processing_ms':round((time.monotonic()-started)*1000,3),'peer':self.client_address[0]})
    return Handler


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--role',required=True,choices=('relay','sink'))
    parser.add_argument('--node',required=True)
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8080)
    parser.add_argument('--next',help='URL del nodo siguiente, solo relay')
    parser.add_argument('--timeout',type=float,default=4.0)
    parser.add_argument('--log',default='data/e03_node.csv')
    a=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9]{1,16}',a.node):parser.error('ID de nodo no valido')
    if a.role=='relay' and not a.next:parser.error('Especificar --next')
    print(f'GEA E03 v2 {a.role.upper()} NODO={a.node} http://{a.host}:{a.port} -> {a.next or "DESTINO"}',flush=True)
    ThreadingHTTPServer((a.host,a.port),factory(a)).serve_forever()
if __name__=='__main__':main()
