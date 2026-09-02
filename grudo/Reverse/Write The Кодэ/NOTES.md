# Write The "Кодэ" — solve notes (571 pts)

## Flag (VERIFIED against live checker)
`grodno{Fabrice_Bellard_is_a_really_cool_programmer}`

## How it works
- dist.zip = modified TCC ("I prefer to change the compiler"): `tcc` binary embeds a custom
  "internal audit library". checker.c references `extern int audit(const char *answer)`.
- Build: `./tcc -B./runtime checker.c -o checker` — works out of the box; `audit` resolves
  from the patched tcc.
- `audit()` (0x402292 in the compiled checker):
  1. `sub_401F92`: "build provenance" — opens `/proc/self/exe`, iterates all section headers,
     and for each SHT_RELA section hashes every relocation:
     `state = rotl64(state ^ (r_info + 0x9E3779B97F4A7C15 + (i<<32) + j), 17) * 0xBF58476D1CE4E5B9`
     then `^= r_addend` (state starts at SHA256 H0 0x6A09E667F3BCC909).
  2. Decodes a 0x200-byte blob (vaddr 0x405B34) with a byte keystream from the in-place mix
     function `sub_40220C` (`^= >>12; ^= <<25; ^= >>27; *= 0x2545F4914F6CDD1D`) seeded with
     that hash. The blob is interpreted, never executed (mprotect RX is a decoy).
  3. Interprets the decoded blob as a per-character state machine. Layout per element (7 bytes):
     `0xA7 marker, add_byte, rot_byte(&31), u32 expected`.
     - `state = 0xC0DEC0DE`
     - `state ^= sign_ext8(answer[i]) + add_byte`   (KEY: movsx, signed!)
     - `state = rotl32(state, rot)`
     - `state += (i*0x45D9F3B) ^ 0x9E3779B9`
     - `state == expected` else reject; require `answer[len]==0`.

## Solve
- Reproduce hash in Python (parse ELF RELA sections exactly as sub_401F92).
- Decode blob, then per element brute-force byte b in 0..255 such that
  `rotl32(state ^ (signext8(b)+add), rot) + mixadd == expected`; chain state.
- First naive attempt (unsigned byte add) failed on live binary — the `movsx` sign extension
  wraps at 2^32 for bytes >= 0x80; verified against gdb trace (state/expected at 0x4025A7).
- Result: 51 printable chars forming the flag. `echo 'grodno{...}' | ./checker` → "accepted".

Files: solve_kode.py (full solver), FLAG.txt.
