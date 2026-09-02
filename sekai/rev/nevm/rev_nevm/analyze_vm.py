from pathlib import Path
OPN={0x5b:'JUMPDEST',0x56:'JUMP',0x57:'JUMPI',0x52:'MSTORE',0x53:'MSTORE8',0x39:'CODECOPY',0x51:'MLOAD',0x35:'CALLDATALOAD',0xf3:'RETURN',0x50:'POP',0x80:'DUP1',0x81:'DUP2',0x82:'DUP3',0x83:'DUP4',0x90:'SWAP1'}

def disasm_at(b, pc, count=80):
    for _ in range(count):
        if pc>=len(b): break
        x=b[pc]
        if 0x60<=x<=0x7f:
            n=x-0x5f; arg=b[pc+1:pc+1+n]
            print(f'{pc:08x}: PUSH{n} 0x{arg.hex()}')
            pc+=1+n
        elif 0x80<=x<=0x8f:
            print(f'{pc:08x}: DUP{x-0x7f}'); pc+=1
        elif 0x90<=x<=0x9f:
            print(f'{pc:08x}: SWAP{x-0x8f}'); pc+=1
        else:
            print(f'{pc:08x}: {OPN.get(x,hex(x))}'); pc+=1

def parse_init(b):
    pc=14 # after codecopy? actually starts first PUSH4 at 0xe
    writes=[]
    # pattern PUSH4 val, then 4 mstore8 to dest..dest+3, optionally repeats
    while pc < len(b):
        if b[pc]!=0x63: break
        val=int.from_bytes(b[pc+1:pc+5],'big'); pc0=pc; pc+=5
        # consume until 4 MSTORE8; record dests from PUSH3 before each MSTORE8
        ds=[]
        for k in range(4):
            # find next 0x53 after a PUSH3 dest near before
            j=pc
            found=False
            while j<pc+40 and j<len(b):
                if b[j]==0x62 and j+4<len(b) and b[j+4]==0x53:
                    ds.append(int.from_bytes(b[j+1:j+4],'big')); pc=j+5; found=True; break
                j+=1
            if not found:
                return writes, pc0
        writes.append((val, ds[0]))
    return writes, pc

for i in [1]:
 b=Path(f'challenge_{i}.dec').read_bytes()
 copy_len=int.from_bytes(b[2:5],'big')
 copy_off=int.from_bytes(b[6:10],'big')
 print('copy_len/off/dest',hex(copy_len),hex(copy_off),hex(0x3000),'endmem',hex(0x3000+copy_len))
 writes,pc=parse_init(b)
 print('handlers',len(writes),'after pc',hex(pc))
 print('first 20 handlers')
 for idx,(addr,dst) in enumerate(writes[:20]): print(idx,hex(dst),hex(addr))
 print('last 10 handlers')
 for idx,(addr,dst) in list(enumerate(writes))[-10:]: print(idx,hex(dst),hex(addr))
 print('disasm after writes')
 disasm_at(b, pc, 120)
