from pwn import *
import struct
import os

gdbscript = """
set pagination off
set logging file gdb.log
set logging enabled on
# Break before main loop
b *main+0x97
# Break at cmd 0x15 (case 5)
b *main+0x522
# Break at cmd 0x16 (case 6)
b *main+0x591
# Break inside FUN_00101361
b *0x1361
b *0x1376
b *0x13a8
b *0x13b5
commands
  info registers
  x/6gx $rbx
  x/6gx $rdi
  continue
end
continue
"""

# Let's run gdb directly with subprocess
import subprocess

p_gdb = subprocess.Popen(['gdb', '-batch', '-x', 'gdb_commands.txt'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
