"""Comprueba la consistencia aritmética del modelo presupuestal proporcionado."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data/modelos/SENTINEL_CAPEX_OPEX_2026.csv'
def validate_budget():
    with PATH.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    sums={'CAPEX':0,'OPEX_mensual':0}
    totals={}
    for row in rows:
        k=row['clasificacion']; q=float(row['cantidad']); unit=float(row['costo_unitario_MXN']);subtotal=float(row['subtotal_MXN'])
        if round(q*unit,2)!=round(subtotal,2):
            raise ValueError(f'Subtotal incompatible en {row["concepto"]}')
        if k in sums:sums[k]+=subtotal
        if k.startswith('TOTAL_') or k=='TCO_36_MESES':totals[k]=subtotal
    capex=int(sums['CAPEX']);opex=int(sums['OPEX_mensual']);tco=int(capex+36*opex)
    if (capex,opex,tco)!=(66800,2140,143840):raise ValueError('No coinciden totales de planeación')
    if (totals['TOTAL_CAPEX'],totals['TOTAL_OPEX_MENSUAL'],totals['TCO_36_MESES'])!=(capex,opex,tco):raise ValueError('Totales escritos inconsistentes')
    return {'capex_MXN':capex,'opex_mensual_MXN':opex,'tco_36_meses_MXN':tco,'nota':'Modelo de ingeniería; no cotizaciones'}
if __name__=='__main__':print(json.dumps(validate_budget(),ensure_ascii=False,indent=2))
