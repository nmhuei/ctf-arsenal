#!/usr/local/bin/python3
import subprocess
import tempfile

print('Enter your code (end with an EOF):')

code = ''
while True:
    line = input('> ')
    if line == 'EOF':
        break
    code += line + '\n'

if code.count('(') > 1 or '{' in code:
    print('🔥🔥🔥')
    exit(1)

with tempfile.NamedTemporaryFile(suffix='.mojo') as tmp:
    tmp.write(code.encode())
    tmp.flush()
    subprocess.run(['/usr/local/bin/mojo', tmp.name])
