"""Independent bit-level GCM audit and generated fixtures; no RAM scan."""
from pathlib import Path
from Crypto.Cipher import AES
import json,struct
P=Path(__file__).resolve().parent
MASK=(1<<128)-1

def mul_reference(a,b):
 z=0;v=b
 for bit in range(127,-1,-1):
  if a>>bit&1:z^=v
  v=(v>>1)^((0xe1<<120) if v&1 else 0)
 return z

def polynomial_product(a,b):
 p=0
 while b:
  if b&1:p^=a
  a<<=1;b>>=1
 return p

def reflect128(v):return int(f'{v:0128b}'[::-1],2)

def mul_polynomial(a,b):
 product=polynomial_product(reflect128(a),reflect128(b));lo=product&MASK;hi=product>>128
 folded=polynomial_product(hi,0x87);lo^=folded&MASK;overflow=folded>>128
 result=lo^polynomial_product(overflow,0x87)
 assert result<=MASK
 return reflect128(result)

def ghash(h,aad,c):
 data=aad+b'\0'*((-len(aad))%16)+c+b'\0'*((-len(c))%16)+struct.pack('>QQ',len(aad)*8,len(c)*8);s=0
 for i in range(0,len(data),16):
  v=s^int.from_bytes(data[i:i+16],'big');x=mul_reference(v,h);assert x==mul_polynomial(v,h);s=x
 return s.to_bytes(16,'big')

def recover(key,aad,c,tag):
 aes=AES.new(key,AES.MODE_ECB);h=int.from_bytes(aes.encrypt(bytes(16)),'big');value=bytes(a^b for a,b in zip(tag,ghash(h,aad,c)));return aes.decrypt(value)

def xor_seq(iv,seq):return (int.from_bytes(iv,'big')^seq).to_bytes(12,'big')

key=bytes(range(16));iv=bytes(range(16,28));cases=[]
for seq,n in enumerate([0,1,7,15,16,17,31,32,33,589,16384]):
 payload=bytes((i*31+17)&255 for i in range(n))+b'\x17';aad=b'\x17\x03\x03'+(len(payload)+16).to_bytes(2,'big');nonce=xor_seq(iv,seq);g=AES.new(key,AES.MODE_GCM,nonce=nonce);g.update(aad);c,tag=g.encrypt_and_digest(payload);j0=recover(key,aad,c,tag);assert j0==nonce+b'\0\0\0\1';assert xor_seq(j0[:12],seq)==iv
 badtag=bytes([tag[0]^1])+tag[1:];badj0=recover(key,aad,c,badtag);assert badj0[-4:]!=b'\0\0\0\1';cases.append({'seq':seq,'content_bytes':n,'passed':True})
fixtures=[]
for seq,payload in [(0,b'GET /fixture HTTP/1.1\r\n\r\n\x17'),(6,b'\x88\x80\x01\x23\x45\x67\x17')]:
 aad=b'\x17\x03\x03'+(len(payload)+16).to_bytes(2,'big');g=AES.new(key,AES.MODE_GCM,nonce=xor_seq(iv,seq));g.update(aad);c,tag=g.encrypt_and_digest(payload);fixtures.append({'seq':seq,'aad':aad.hex(),'ciphertext':c.hex(),'tag':tag.hex(),'plaintext':payload.hex()})
fixture={'key':key.hex(),'base_iv':iv.hex(),'records':fixtures,'kind':'generated offline fixture; no captured secrets'};(P/'gcm_audit_fixture.json').write_text(json.dumps(fixture,indent=2));report={'cases':cases,'ghash_implementations_agree':True,'nonce_recovery_passed':True,'seq_iv_consistency_passed':True,'corrupt_tags_rejected':True};(P/'gcm_math_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
