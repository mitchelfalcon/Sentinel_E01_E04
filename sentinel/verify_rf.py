"""Validar bitácora recibida de nodos RF externos. NO crea comunicaciones RF."""
import csv,argparse,collections,json
from pathlib import Path
FIELDS=['run_id','radio_model','firmware','frequency_mhz','node','sequence','status','hop','peer','rssi_dbm','snr_db','utc','mono_ms','route','packet_sha256','los','distance_m']

def verify(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f);missing=set(FIELDS)-set(r.fieldnames or [])
        if missing:raise ValueError('Columnas faltantes: '+','.join(sorted(missing)))
        records=list(r)
    issues=[];by=collections.defaultdict(list)
    for i,r in enumerate(records,2):
        try:
            n=int(r['sequence']); hop=int(r['hop']);float(r['frequency_mhz']);float(r['mono_ms'])
            if hop<0:issues.append(f'linea {i}: hop negativo')
            if len(r['packet_sha256'])!=64:issues.append(f'linea {i}: hash SHA256 invalido')
            if not r['radio_model'].strip():issues.append(f'linea {i}: radio_model vacio')
            by[(r['run_id'],n)].append(r)
        except ValueError:issues.append(f'linea {i}: valor numerico invalido')
    chains=0
    for key,ev in by.items():
        hops={int(x['hop']) for x in ev if x['hop'].isdigit() and x['status'].upper()=='RX'}
        if len(hops)>=2:chains+=1
        hashes={x['packet_sha256'] for x in ev}
        if len(hashes)>1:issues.append(f'{key}: hashes divergentes')
    return {'records':len(records),'sequences':len(by),'sequences_with_2_or_more_rx_hops':chains,'issues':issues,'warning':'CSV es declaración instrumental, no prueba por sí solo que los radios se conectaron; adjuntar registros de hardware/firmware/fotos sin datos sensibles.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('csv');a=p.parse_args();r=verify(a.csv);print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(1 if r['issues'] else 0)
if __name__=='__main__':main()
