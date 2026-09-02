from sympy import randprime
from random import randint

def generate_basis(n):
    basis=[True]*n
    for i in range(3,int(n**0.5)+1,2):
        if basis[i]:
            basis[i*i::2*i]=[False]*((n-i*i-1)//(2*i)+1)
    return [2]+[i for i in range(3,n,2) if basis[i]]

def mr(n):
    if n in (2,3): return True
    if n%2==0: return False
    r,s=0,n-1
    while s%2==0:
        r+=1; s//=2
    for b in generate_basis(64):
        x=pow(b,s,n)
        if x in (1,n-1): continue
        for _ in range(r-1):
            x=pow(x,2,n)
            if x==n-1: break
        else: return False
    return True
