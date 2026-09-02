#!/usr/bin/env python3
"""
angr solver for r3fake/lift - byte-by-byte approach.
Solve one symbolic byte at a time, keeping known bytes concrete.
"""

import angr
import claripy
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger(__name__)

BINARY_PATH = '/home/light/Workspace/CTF/r3fake/lift/chall'
FLAG_LEN = 39
PREFIX = b"R3CTF{"
PREFIX_LEN = len(PREFIX)
CONTENT_LEN = 32


class FgetsHook(angr.SimProcedure):
    """Hook for fgets: write prefix + known content + one symbolic byte + trailing '}'"""
    def run(self, buf, size, stream):
        # Write known prefix
        for i, b in enumerate(PREFIX):
            self.state.memory.store(buf + i, claripy.BVV(b, 8))

        # Write known content (concrete so far)
        known = self.state.globals.get('known_content', b'')
        symbolic_pos = self.state.globals.get('symbolic_pos', 0)

        for i in range(min(len(known), CONTENT_LEN)):
            self.state.memory.store(buf + PREFIX_LEN + i, claripy.BVV(known[i], 8))

        # One symbolic byte at the current position
        if symbolic_pos < CONTENT_LEN:
            byte = claripy.BVS(f'char_{symbolic_pos}', 8)
            self.state.solver.add(claripy.And(byte >= 0x20, byte <= 0x7e))
            self.state.memory.store(buf + PREFIX_LEN + symbolic_pos, byte)
            self.state.globals['flag_byte'] = byte

        # Fill remaining with 'A' (concrete padding)
        for i in range(symbolic_pos + 1, CONTENT_LEN):
            self.state.memory.store(buf + PREFIX_LEN + i, claripy.BVV(ord('A'), 8))

        # Closing brace
        self.state.memory.store(buf + FLAG_LEN - 1, claripy.BVV(ord('}'), 8))
        self.state.memory.store(buf + FLAG_LEN, claripy.BVV(0, 8))

        return buf


def solve_one_byte(proj, base, known_content, sym_pos):
    """Solve for one byte at position sym_pos, given known_content for previous bytes."""
    log.info(f"\n{'='*60}")
    log.info(f"Solving byte {sym_pos} (known so far: {known_content.decode()!r})")

    # Re-hook fgets for this iteration
    proj.hook_symbol('fgets', FgetsHook(), replace=True)
    # Hook setrlimit/getrlimit
    proj.hook_symbol('setrlimit', angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())
    proj.hook_symbol('getrlimit', angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())

    # Key addresses
    addr_correct = base + 0x21eb5e
    addr_avoid = [
        base + 0x21eb87, base + 0x21ec47, base + 0x21eca2, base + 0x21eced,
    ]

    # Start at main
    addr_main = base + 0x21ebcf
    state = proj.factory.blank_state(
        addr=addr_main,
        add_options={
            angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
            angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
        },
    )

    STACK_BASE = 0x7fffffffffeff00
    state.regs.rsp = STACK_BASE
    state.regs.rbp = STACK_BASE
    state.regs.rdi = 1
    state.regs.rsi = 0
    state.regs.rdx = 0

    # Pass known content and position via globals
    state.globals['known_content'] = known_content
    state.globals['symbolic_pos'] = sym_pos

    # Explore
    sm = proj.factory.simulation_manager(state)

    log.info(f"Exploring byte position {sym_pos}...")
    start = time.time()

    try:
        sm.explore(find=addr_correct, avoid=addr_avoid, num_find=1)
    except Exception as e:
        log.error(f"Explore error: {e}")
        return None

    elapsed = time.time() - start
    log.info(f"Explore: {elapsed:.2f}s, active={len(sm.active)}, found={len(sm.found)}, avoid={len(sm.avoid)}")

    if sm.found:
        found = sm.found[0]
        byte_bvs = found.globals.get('flag_byte')
        if byte_bvs is not None:
            try:
                byte_val = found.solver.eval(byte_bvs)
                char = chr(byte_val)
                log.info(f"Byte {sym_pos} = '{char}' (0x{byte_val:02x})")
                return char
            except Exception as e:
                log.error(f"Eval error: {e}")

    # If not found, try the avoid states to get partial information
    if sm.avoid:
        log.info("Checking avoid states for constraint info...")

    return None


def main():
    proj = angr.Project(BINARY_PATH, auto_load_libs=False)
    base = proj.loader.main_object.mapped_base
    log.info(f"PIE base: 0x{base:x}")

    known = b""
    for pos in range(CONTENT_LEN):
        char = solve_one_byte(proj, base, known, pos)
        if char is None:
            log.warning(f"Failed to solve byte {pos}")
            break
        known += char.encode()

    flag = "R3CTF{" + known.decode() + "}"
    log.info(f"\n{'='*60}")
    log.info(f"FLAG: {flag}")
    print(f"\n{'='*60}")
    print(f"FLAG: {flag}")
    print(f"{'='*60}")

    return flag


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result else 1)
