#!/usr/bin/env python3
"""Full solve script in Python"""
import socket, ssl, hashlib, json, urllib.request, re, sys, time, struct
from nacl.bindings import crypto_sign_seed_keypair
from base64 import b64encode

HOST = 'open-world-ad339fb35916.instancer.sekai.team'
PORT = 1337

# === Step 1: Get session ===
print('[1] Getting session...', file=sys.stderr)
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
sock = socket.create_connection((HOST, PORT), timeout=30)
ssock = ctx.wrap_socket(sock, server_hostname=HOST); ssock.settimeout(30)

buf = b''
while b'action?' not in buf: buf += ssock.recv(4096)
ssock.send(b'1\n')
buf = b''
while b'YOUR_INPUT = ' not in buf: buf += ssock.recv(4096)
text = buf.decode()
prefix = re.search(r'sha256\("([^"]+)"', text).group(1)
diff = int(re.search(r'(\d+) bytes zeros', text).group(1))

print(f'  PoW: prefix={prefix}, difficulty={diff}', file=sys.stderr)
target = '0' * (diff * 2)
nonce = 0
while True:
    h = hashlib.sha256((prefix + str(nonce)).encode()).hexdigest()
    if h.startswith(target): break
    nonce += 1
print(f'  PoW solved: {nonce}', file=sys.stderr)
ssock.send((str(nonce) + '\n').encode())

buf = b''
while b'seed:' not in buf: buf += ssock.recv(4096)
text = buf.decode(); ssock.close()

s = {}
for line in text.split('\n'):
    if ':' in line:
        k, v = line.split(':', 1)
        s[k.strip().lower().replace(' ', '_'] = v.strip()

api = s['api_v2'].rstrip('/')
challenge = s['challenge_contract']
wallet_id = int(s['your_wallet_id'])
seed_hex = s['seed']
uuid = s['uuid']
print(f'  UUID: {uuid}', file=sys.stderr)
print(f'  Challenge: {challenge}', file=sys.stderr)

def call(method, params):
    payload = json.dumps({'id':'1','jsonrpc':'2.0','method':method,'params':params}).encode()
    req = urllib.request.Request(api+'/jsonRPC', data=payload, headers={'Content-Type':'application/json'})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=10).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

# === Step 2: Create wallet ===
print('[2] Creating wallet...', file=sys.stderr)
seed = bytes.fromhex(seed_hex)
pk, sk = crypto_sign_seed_keypair(seed)

# Use pytoniq for wallet address computation
# But let me use a simpler approach: derive the address manually
# The wallet contract code is standard, just compute the hash

# Actually, let's use @ton/ton via subprocess for TON interaction
# Or let's just copy the needed functions

# First, check challenge balance
print('[3] Checking initial state...', file=sys.stderr)
info = call('getAddressInformation', {'address': challenge})
challenge_bal = int(info['result']['balance'])
print(f'  Challenge balance: {challenge_bal/1e9} TON', file=sys.stderr)

# Get minter address
minter_resp = call('runGetMethod', {'address': challenge, 'method': 'minter', 'stack': []})
# The minter address is returned as a cell, need to parse it
# From the stack: ['cell', {'bytes': '...', 'object': ...}]
minter_cell = minter_resp['result']['stack'][0][1]
minter_b64 = minter_cell['object']['data']['b64']
# Parse the address from BOC
print(f'  Minter address cell: {minter_b64[:40]}...', file=sys.stderr)

# Save session for TypeScript
json.dump({
    'uuid': uuid,
    'challenge': challenge,
    'api': api,
    'wallet_version': 'v3r2',
    'wallet_id': wallet_id,
    'seed': seed_hex,
}, open('session.json', 'w'))
print(f'  Session saved to session.json', file=sys.stderr)
