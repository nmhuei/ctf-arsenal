#!/usr/bin/env python3
"""Get fresh session, check challenge balance"""
import socket, ssl, hashlib, json, urllib.request, re, sys, time

HOST = 'open-world-ad339fb35916.instancer.sekai.team'
PORT = 1337

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

sock = socket.create_connection((HOST, PORT), timeout=30)
ssock = ctx.wrap_socket(sock, server_hostname=HOST)
ssock.settimeout(30)

# Get session
buffer = b''
while b'action?' not in buffer:
    buffer += ssock.recv(4096)
ssock.send(b'1\n')

buffer = b''
while b'YOUR_INPUT = ' not in buffer:
    buffer += ssock.recv(4096)
text = buffer.decode()
m = re.search(r'sha256\("([^"]+)"', text)
prefix = m.group(1)
d = re.search(r'(\d+) bytes zeros', text)
diff = int(d.group(1)) if d else 3
target = '0' * (diff * 2)

nonce = 0
while True:
    h = hashlib.sha256((prefix + str(nonce)).encode()).hexdigest()
    if h.startswith(target):
        break
    nonce += 1
print(f'PoW solved: {nonce}', file=sys.stderr)
ssock.send((str(nonce) + '\n').encode())

buffer = b''
while b'seed:' not in buffer:
    buffer += ssock.recv(4096)
text = buffer.decode()
ssock.close()

# Parse
session = {}
for line in text.split('\n'):
    if ':' in line:
        k, v = line.split(':', 1)
        session[k.strip().lower().replace(' ', '_'] = v.strip()

for k, v in session.items():
    print(f'  {k}: {v}', file=sys.stderr)

api = session.get('api_v2', '').rstrip('/')
challenge = session['challenge_contract']

def call(method, params):
    payload = json.dumps({'id':'1','jsonrpc':'2.0','method':method,'params':params}).encode()
    req = urllib.request.Request(api+'/jsonRPC', data=payload, headers={'Content-Type':'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

# Check challenge balance
info = call('getAddressInformation', {'address': challenge})
bal = int(info['result']['balance'])
print(f'Challenge balance: {bal} nanoTON = {bal/1e9} TON')

# Save session
session['api'] = session.get('api_v2', session.get('api_v2', ''))
for k in list(session.keys()):
    if 'api' in k:
        session['api'] = session[k]
        break

json.dump(session, open('session.json', 'w'))
print(f'Saved session {session.get("uuid","?")}', file=sys.stderr)
