from Crypto.Util.number import getPrime, bytes_to_long
import random



rbit = 444
pbit = 512

p = bytes_to_long(open('flag','rb').read())

xs = [p * getPrime(pbit) + random.randint(1,2**rbit) for _ in range(10)]

open('output.py', 'w').write(f'xs = {str(xs)}')