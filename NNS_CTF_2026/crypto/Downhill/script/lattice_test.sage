import json
data=json.load(open('/tmp/downhill_sim.json'))
N=251; q=128
f=data['f']+[0]*(N-len(data['f']))
g=data['g']+[0]*(N-len(data['g']))
h=data['h']+[0]*(N-len(data['h']))
H=matrix(ZZ,N,N,lambda i,j: h[(j-i)%N])
B=block_matrix(ZZ, [[identity_matrix(ZZ,N), H], [zero_matrix(ZZ,N,N), q*identity_matrix(ZZ,N)]])
print('building LLL', B.nrows(), B.ncols())
L=B.LLL(delta=0.99)
print('done')
target=vector(ZZ,f+g)
for i in range(min(30,L.nrows())):
    v=L.row(i)
    print(i, v.norm(), 'dots', abs(v.dot_product(target)), 'nz', sum(x!=0 for x in v))
    if v.dot_product(target) > 0.9*target.norm()^2 or (-v).dot_product(target)>0.9*target.norm()^2:
        print('candidate', list(v))
