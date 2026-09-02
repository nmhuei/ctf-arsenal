#!/usr/bin/env python3
S=22263691028918788395010325066307464924652601045336492930678310479674861811846
def solve():
    f=lambda n:n//2-n//59051
    lo,hi=0,10**100
    while lo<hi:
        m=(lo+hi)//2
        if f(m)<S: lo=m+1
        else: hi=m
    for n in range(lo-5,lo+6):
        if f(n)==S:
            flag=n.to_bytes((n.bit_length()+7)//8,'big').decode()
            print('FLAG:',flag)
            return flag
if __name__=='__main__': solve()
