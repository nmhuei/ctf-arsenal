from pathlib import Path
MASK=0xffffffff;GOLD=0x9e3779b9

def hkey(key):
 h=0
 for c in key.encode():h=((((h<<5)|(h>>27))&MASK)^c)*GOLD&MASK
 h=h*GOLD&MASK
 if h<2:h=(h-2)&MASK
 return h&~1

def key(host,partition='coccoc.com'):
 p='^partitionKey=%28https%2C'+partition+'%29'
 return f'https:{host}:443:.:{p}:3'

if __name__=='__main__':
 lines=Path('script/offline_audit/root_files/37_AlternateServices.partial.txt').read_text().splitlines()[1:]
 for l in lines:
  k=l.split('\t')[0];h=hkey(k);print(h>>27,h>>26,h>>25,k.split(':')[1])
