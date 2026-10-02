#!/bin/bash
gdb -nx -batch -x /home/light/Workspace/CTF/CSCV_2026_Quals/Pwn/sinkhole/script/pure_gdb.txt --args "$@"
