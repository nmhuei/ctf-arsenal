import gdb
import struct

# GDB python script
gdb.execute("set pagination off")
gdb.execute("set exec-wrapper ./ld-linux-x86-64.so.2 --library-path .")
gdb.execute("file ./rwengine")
gdb.execute("b *main")
gdb.execute("run")

# Let's break at FUN_00101361 entry and main switch
# Find main address
main_addr = int(gdb.parse_and_eval("&main"))
print(f"main_addr = {hex(main_addr)}")
base_addr = main_addr - 0x15ad
print(f"base_addr = {hex(base_addr)}")

fun_1361 = base_addr + 0x1361
dat_19880 = base_addr + 0x19880

gdb.execute(f"b *{hex(fun_1361)}")
gdb.execute(f"b *{hex(base_addr + 0x13a8)}")
gdb.execute(f"b *{hex(base_addr + 0x13b5)}")

# Continue and trace
print("Breakpoints set, continuing...")
