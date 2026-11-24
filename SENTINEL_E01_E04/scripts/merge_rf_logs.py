"""Unir registros instrumentales de radios E04 sin alterar sus marcas de tiempo."""
import argparse,csv,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sentinel.verify_rf import FIELDS,verify

def main():
    p=argparse.ArgumentParser()
    p.add_argument('csv',nargs='+',help='Bitácoras RF de A B C [D]')
    p.add_argument('--out',required=True)
    a=p.parse_args()
    rows=[]
    for file in a.csv:
        with Path(file).open(encoding='utf-8-sig',newline='') as fh:
            r=csv.DictReader(fh)
            if set(r.fieldnames or [])-set(FIELDS):raise ValueError(f'{file}: columnas no permitidas')
            if set(FIELDS)-set(r.fieldnames or []):raise ValueError(f'{file}: campos ausentes')
            rows.extend(list(r))
    pth=Path(a.out);pth.parent.mkdir(parents=True,exist_ok=True)
    with pth.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    print('Bitácoras fusionadas:',len(rows),'filas')
    print(verify(pth))
if __name__=='__main__':main()
