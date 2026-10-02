from sage.all import ZZ,next_prime
from pathlib import Path
import subprocess,json
M=ZZ(31721752939659896617792337171084495768312741523809821454149295955199893657462682088273)
for a in (0,1,137,12345678,21621599):
 r=pow(ZZ(17),a,M);k=(2**384-2**379)//M
 while not (r+M*k).is_prime():k+=1
 p=r+M*k;q=next_prime(2**384-2**380+123456789)
 result=Path('script/synthetic_factors.json')
 run=subprocess.run(['script/residue_search',str(p*q),str(a),str(a+1),str(result)],capture_output=True,text=True)
 assert run.returncode==0,run.stderr
 data=json.loads(result.read_text())
 assert data['p']==p and data['q']==q and data['a']==a
 print('synthetic residue test passed',a,flush=True)
