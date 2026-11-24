"""E04-S: modelo parametrizado de sensibilidad LOS/NLOS. No son mediciones RF."""
from __future__ import annotations
import argparse,csv,json,random
from pathlib import Path
from sentinel.analyze import wilson95

DISTANCES_KM=(0.1,0.5,1.0,2.5,5.0)
P_LINK={
    'LOS':(0.995,0.99,0.98,0.94,0.82),
    'NLOS':(0.98,0.94,0.83,0.56,0.30),
}

def simulate_distance(seed=20261123,n_per_condition=200):
    if n_per_condition<=0:raise ValueError('n_per_condition debe ser positivo')
    rng=random.Random(seed)
    observations=[];summary=[]
    for cond,probs in P_LINK.items():
        for distance,p in zip(DISTANCES_KM,probs):
            ok_count=0
            for seq in range(1,n_per_condition+1):
                ok=int(rng.random()<p)
                ok_count+=ok
                observations.append({'modelo':'E04-S_PARAMETRICO_NO_RF','seed':seed,'condicion':cond,
                  'distancia_km':distance,'probabilidad_configurada':p,'intento':seq,'entregado':ok})
            low,high=wilson95(ok_count,n_per_condition)
            summary.append({'modelo':'E04-S_PARAMETRICO_NO_RF','seed':seed,'condicion':cond,
              'distancia_km':distance,'probabilidad_configurada':p,'n':n_per_condition,
              'entregados':ok_count,'pdr_pct':round(100*ok_count/n_per_condition,2),
              'ic95_wilson_inferior_pct':low,'ic95_wilson_superior_pct':high})
    return observations,summary

def dump(folder='runs/e04_sensibilidad',seed=20261123,n_per_condition=200):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    obs,summ=simulate_distance(seed,n_per_condition)
    for path,rows in [(folder/'eventos_modelados.csv',obs),(folder/'pdr_por_distancia.csv',summ)]:
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    (folder/'configuracion.json').write_text(json.dumps({'procedencia':'SIMULACION_PARAMETRICA_NO_RF','seed':seed,'n_por_punto':n_per_condition,
         'distancias_km':DISTANCES_KM,'probabilidades_asumidas':P_LINK,
         'descripcion':'Barrido de sensibilidad matematico: probabilidades elegidas como hipotesis, no estimadas de campo.'},indent=2,ensure_ascii=False),encoding='utf-8')
    return summ

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=20261123)
    parser.add_argument('--n',type=int,default=200);parser.add_argument('--output-dir',default='runs/e04_sensibilidad')
    a=parser.parse_args();print(json.dumps(dump(a.output_dir,a.seed,a.n),indent=2,ensure_ascii=False))
if __name__=='__main__':main()
