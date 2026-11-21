"""E04 banco físico UART-SubGHz (Linux/macOS): nodos transparentes UART, SIN internet.

Advertencia instrumental: transporte UART entre radios configurados NO implica
mesh auto-enrutada. El ensayo RF multisalto debe probar aislamiento A-C, y los
radios/firmwares deben ser compatibles. No integra centros de emergencia.
"""
from __future__ import annotations
import argparse,base64,csv,hashlib,os,re,select,struct,sys,threading,time,zlib
try:
    import termios  # Solo en el adaptador UART POSIX
except ImportError:
    termios = None
from datetime import datetime,timezone
from pathlib import Path

MAGIC=b'S4'; VERSION=1; BODY_LEN=21
FRAME=struct.Struct('!2sBBBBBB21sI')
K_SOS=1;K_FIRST_ACK=2;K_DELIVERY_ACK=3;K_OPERATOR_ACK=4
KINDS={1:'SOS',2:'RECIBIDO',3:'ENTREGADO',4:'ATENDIDO_SIMULADO'}
FIELDS=['run_id','radio_model','firmware','frequency_mhz','node','sequence','status','hop','peer','rssi_dbm','snr_db','utc','mono_ms','route','packet_sha256','los','distance_m','detail']

def payload21(alias='LUNA',seq=1,stamp=0):
    if not re.fullmatch(r'[A-Z0-9]{1,6}',alias):raise ValueError('alias inválido')
    x=bytearray(21);x[:2]=b'\x02\x03';x[2:8]=alias.encode().ljust(6,b'\0')
    struct.pack_into('!II',x,8,seq,stamp);x[16]=0
    struct.pack_into('!I',x,17,zlib.crc32(x[:17])&0xffffffff)
    return bytes(x)

def decode21(x):
    if len(x)!=21 or x[:2]!=b'\x02\x03':raise ValueError('encabezado/carga inválida')
    alias=x[2:8].rstrip(b'\0').decode('ascii');seq,stamp=struct.unpack_from('!II',x,8)
    if (zlib.crc32(x[:17])&0xffffffff)!=struct.unpack_from('!I',x,17)[0]:raise ValueError('CRC32 de carga no coincide')
    return dict(alias=alias,sequence=seq,stamp=stamp,sha256=hashlib.sha256(x).hexdigest())

def pack(kind,origin,forwarder,hop,ttl,payload):
    if kind not in KINDS or not (0<=hop<=10 and 0<=ttl<=10):raise ValueError('tipo o hop/ttl inválido')
    decode21(payload)
    data=FRAME.pack(MAGIC,VERSION,kind,ord(origin),ord(forwarder),hop,ttl,payload,0)
    check=zlib.crc32(data[:-4])&0xffffffff
    return data[:-4]+struct.pack('!I',check)

def unpack(raw):
    if len(raw)!=FRAME.size:raise ValueError('trama UART incorrecta')
    magic,version,kind,origin,forwarder,hop,ttl,payload,check=FRAME.unpack(raw)
    if magic!=MAGIC or version!=VERSION or kind not in KINDS:raise ValueError('formato inválido')
    if zlib.crc32(raw[:-4])&0xffffffff!=check:raise ValueError('CRC32 trama incorrecto')
    pkt=decode21(payload)
    return dict(kind=kind,origin=chr(origin),forwarder=chr(forwarder),hop=hop,ttl=ttl,payload=payload,packet=pkt)

def baud_const(baud):
    if termios is None:raise RuntimeError('UART por termios requiere Linux/macOS; en Windows se necesita adaptador específico')
    name='B'+str(baud)
    if not hasattr(termios,name):raise ValueError('baud no admitido por termios: '+str(baud))
    return getattr(termios,name)

def open_uart(device,baud):
    fd=os.open(device,os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
    attrs=termios.tcgetattr(fd)
    attrs[0]=0;attrs[1]=0;attrs[2]|=termios.CLOCAL|termios.CREAD;attrs[3]=0
    attrs[4]=baud_const(baud);attrs[5]=baud_const(baud)
    attrs[6][termios.VMIN]=0;attrs[6][termios.VTIME]=1
    termios.tcsetattr(fd,termios.TCSANOW,attrs)
    return fd

def main(argv=None):
    p=argparse.ArgumentParser(description='Puente UART transparente para E04 sin Internet (solo laboratorio)')
    p.add_argument('--role',choices=['source','relay','sink'],required=True)
    p.add_argument('--node',choices=['A','B','C','D'],required=True)
    p.add_argument('--device',required=True,help='p.ej. /dev/ttyUSB0')
    p.add_argument('--baud',type=int,default=9600)
    p.add_argument('--run-id',default='E04-RF-LOCAL')
    p.add_argument('--radio-model',default='MODELO_POR_DECLARAR')
    p.add_argument('--firmware',default='VERSION_POR_DECLARAR')
    p.add_argument('--frequency-mhz',type=float,default=915)
    p.add_argument('--los',default='NO_MEDIDO')
    p.add_argument('--distance-m',default='')
    p.add_argument('--n',type=int,default=10)
    p.add_argument('--interval',type=float,default=2.0)
    p.add_argument('--duration',type=float,default=50.0)
    p.add_argument('--log',default=None)
    p.add_argument('--allow-direct-at-sink',action='store_true',help='Solo control; no usar para validar multihop')
    a=p.parse_args(argv)
    if a.role=='source' and a.node!='A':p.error('el emisor de referencia es A')
    if a.role=='sink' and a.node!='C':p.error('la estación de referencia es C')
    if a.role=='relay' and a.node not in ('B','D'):p.error('el relay debe ser B o D')
    if a.interval<=0 or a.duration<=0 or a.n<0:p.error('valores de tiempo/n inválidos')
    path=Path(a.log or f'runs/e04_{a.node}.csv');path.parent.mkdir(exist_ok=True,parents=True)
    fd=open_uart(a.device,a.baud)
    file=path.open('w',newline='',encoding='utf-8');writer=csv.DictWriter(file,fieldnames=FIELDS);writer.writeheader();file.flush()
    started=time.monotonic();buf=b'';seen=set();last={};lock=threading.Lock()
    def log(status,msg,peer='',detail=''):
        pkt=msg['packet'];rec={'run_id':a.run_id,'radio_model':a.radio_model,'firmware':a.firmware,'frequency_mhz':a.frequency_mhz,'node':a.node,'sequence':pkt['sequence'],'status':status,'hop':msg['hop'],'peer':peer or msg['forwarder'],'rssi_dbm':'','snr_db':'','utc':datetime.now(timezone.utc).isoformat(),'mono_ms':round((time.monotonic()-started)*1000,3),'route':f"{msg['origin']}>{msg['forwarder']}>{a.node}",'packet_sha256':pkt['sha256'],'los':a.los,'distance_m':a.distance_m,'detail':detail}
        with lock:writer.writerow(rec);file.flush()
        print(f"[{a.node}] {status} seq={pkt['sequence']} hop={msg['hop']} {detail}",flush=True)
    def send(kind,payload,origin,hop,ttl,detail=''):
        raw=pack(kind,origin,a.node,hop,ttl,payload)
        # El modem debe transportar exactamente líneas ASCII, sin alterar base64.
        line=base64.urlsafe_b64encode(raw)+b'\n'
        with lock:os.write(fd,line)
        msg=unpack(raw);log('TX',msg,a.node,detail)
    def operator():
        while True:
            try:line=input(f'[{a.node}] Para confirmar revisión simulada: atender <secuencia>\n')
            except EOFError:return
            parts=line.lower().split()
            if len(parts)==2 and parts[0]=='atender' and parts[1].isdigit():
                seq=int(parts[1]);pay=last.get(seq)
                if pay is None:print('Secuencia no recibida',flush=True);continue
                send(K_OPERATOR_ACK,pay,'A',2,4,'Confirmación de operador de laboratorio')
    if a.role=='sink':threading.Thread(target=operator,daemon=True).start()
    next_send=time.monotonic()+.6;idx=1
    try:
        while time.monotonic()-started<a.duration:
            if a.role=='source' and idx<=a.n and time.monotonic()>=next_send:
                data=payload21('LUNA',idx,int(time.time()))
                send(K_SOS,data,'A',0,4,'SOS sintético');idx+=1;next_send=time.monotonic()+a.interval
            readable,_,_=select.select([fd],[],[],.12)
            if not readable:continue
            chunk=os.read(fd,4096)
            if not chunk:continue
            buf+=chunk
            if len(buf)>16000:buf=b'';continue
            while b'\n' in buf:
                line,buf=buf.split(b'\n',1)
                try:msg=unpack(base64.urlsafe_b64decode(line.strip()))
                except Exception as e:print('[DESCARTE UART]',str(e),flush=True);continue
                key=(msg['kind'],msg['origin'],msg['packet']['sequence'],msg['forwarder'],msg['hop'])
                if key in seen:continue
                seen.add(key)
                if msg['forwarder']==a.node:continue
                if msg['kind']==K_SOS:
                    log('RX',msg,detail='SOS recibido por radio serial')
                    if a.role=='relay' and msg['ttl']>1 and msg['hop']==0:
                        send(K_FIRST_ACK,msg['payload'],msg['origin'],1,4,'ACK primer receptor')
                        time.sleep(.10)
                        send(K_SOS,msg['payload'],msg['origin'],msg['hop']+1,msg['ttl']-1,'Relé RF; falta aislar enlace A-C')
                    elif a.role=='sink':
                        if msg['hop']==0 and not a.allow_direct_at_sink:
                            log('DIRECTO_IGNORADO',msg,detail='No válido para ensayo multihop');continue
                        last[msg['packet']['sequence']]=msg['payload']
                        log('ENTREGADO',msg,detail='Paquete aceptado en estación')
                        send(K_DELIVERY_ACK,msg['payload'],msg['origin'],msg['hop']+1,4,'ACK estación')
                elif msg['kind'] in (K_FIRST_ACK,K_DELIVERY_ACK,K_OPERATOR_ACK):
                    if a.role=='source':log(KINDS[msg['kind']],msg,detail='ACK recibido en emisor')
                    elif a.role=='relay' and msg['kind'] in (K_DELIVERY_ACK,K_OPERATOR_ACK) and msg['forwarder']=='C':
                        log('RX',msg,detail='ACK retorno');send(msg['kind'],msg['payload'],'A',msg['hop']+1,msg['ttl']-1,'ACK retransmitido hacia origen')
    except KeyboardInterrupt:pass
    finally:
        file.close();os.close(fd)
        print('CSV guardado:',path,flush=True)
if __name__=='__main__':main()
