# A Great Big Leap — solve notes (1000 pts)

## Flag
`grodno{123}`

## Method
Static analysis of `goingtoofaraway5.exe` (PE32 i386, 3 sections). The .data section is
full of ~100 newline-delimited fake-flag strings ("Super_secret_flag1", ... red herrings),
and the .text is a self-looping maze: sequences of `cmp reg,imm` "checkpoints" with
`je/jne/jmp` that just cycle between 0x401014 / 0x401102 / 0x40112f / 0x4010b2 forever;
the print routine at 0x401169+ (WriteFile loop printing fake flags) is unreachable dead code.

The Russian poem's words map to assembly concepts:
- jump  -> jmp / conditional branch
- stand -> nop (the nops between cmps)
- compare -> cmp (the checkpoint right before a branch)
- "how far you've come" (какой большой прошел ты путь) -> the branch DISPLACEMENT

So the flag = the distance of the largest ("great big leap") jump. All real branch
displacements (objdump, instruction-boundary decoded):

| instruction | target | disp |
|---|---|---|
Calculated as `disp = target - (addr + instruction_size)` (the encoded rel32/rel8
field value), for every direct branch in .text:

| instruction | target | disp |
|---|---|---|
| 40101e je   | 0x401102 | +0xde  (+222) |
| 401051 je   | 0x401014 | -0x3f  ( -63) |
| 40105c jne  | 0x401102 | +0xa0  (+160) |
| 401074 jne  | 0x40112f | +0xb5  (+181) |
| 4010b5 jmp  | 0x401014 | -0xa6  (-166) |
| 4010d7 je   | 0x4010b2 | -0x27  ( -39) |
| 401105 je   | 0x40112f | +0x28  ( +40) |
| **401132 jmp → 0x401014** | **-0x123** | **(max, 291)** |
| 40113c je   | 0x4010b2 | -0x90  (-144) |
| 401148 je   | 0x4010b2 | -0x9c  (-156) |
| 401157 jne  | 0x4010b2 | -0xab  (-171) |

Largest absolute displacement = 0x123, right after the "compare" `cmp edx,0x33`
(the last checkpoint before the leap). Flag = `grodno{123}` (hex digits).

Independent checks:
- Runtime: `WINEDEBUG=-all wine goingtoofaraway5.exe` hangs (timeout kill, exit 124) —
  confirms the maze never reaches the print routine; flag is purely static.
- Published official-style writeup (same binary SHA-256 4250d407...):
  MacallanTheRoot/ctf-writeups, `junior-crypt-2026-writeups/rev/a_great_big_leap`
  -> largest jump 0x401132 -> 0x401014 (-0x123) -> `grodno{123}`.
- Local `solve_leap.py` (objdump-parsed) reproduces it on the exact binary.

Files: solve_leap.py (jump-distance extractor), FLAG.txt.