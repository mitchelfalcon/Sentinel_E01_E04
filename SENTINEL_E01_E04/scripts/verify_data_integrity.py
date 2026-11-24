"""Comprobar hashes SHA-256 de datos observados al compartir o mover el ZIP."""
import hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'data/observados/SHA256SUMS.txt'
errors=[]
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip() or line.startswith('#'):continue
    digest,name=line.split('  ',1)
    src=ROOT/'data/observados'/name
    if not src.is_file():errors.append(f'{name}: archivo no presente');continue
    current=hashlib.sha256(src.read_bytes()).hexdigest()
    if current!=digest:errors.append(f'{name}: HASH DISTINTO')
if errors:
    print('\n'.join(errors));sys.exit(1)
print('OK: SHA-256 de datos observados coincide con manifiesto')
