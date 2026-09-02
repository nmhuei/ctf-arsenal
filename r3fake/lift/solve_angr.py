#!/usr/bin/env python3
"""
angr solver for r3fake/lift - FINAL attempt.
Simple exploration from main with lazy solves and prioritization.
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

def main():
    log.info("Loading binary: %s", BINARY_PATH)
    proj = angr.Project(BINARY_PATH, auto_load_libs=False)
    base = proj.loader.main_object.mapped_base
    log.info("PIE base: 0x%x", base)

    proj.hook_symbol('setrlimit', angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())
    proj.hook_symbol('getrlimit', angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())

    addr_correct = base + 0x21eb5e
    addr_avoid = [
        base + 0x21eb87, base + 0x21ec47, base + 0x21eca2, base + 0x21eced,
    ]

    # Start at entry point _start (let everything initialize properly)
    addr_start = base + 0x1100

    state = proj.factory.blank_state(
        addr=addr_start,
        add_options={
            angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
            angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
        },
    )

    state.regs.rsp = 0x7fffffffffeff00
    state.regs.rdi = 1  # argc
    state.regs.rsi = 0  # argv

    # Create symbolic stdin
    stdin_content = claripy.BVS('stdin', 256 * 8)
    state.posix.files[0] = angr.storage.file.SimFile(
        '/dev/stdin', content=stdin_content, has_end=True
    )

    sm = proj.factory.simulation_manager(state)

    # Use DFS to go deep into one path
    sm.use_technique(angr.exploration_techniques.DFS())

    log.info("Starting exploration (DFS)...")
    log.info("This will take a while due to obfuscation")

    try:
        sm.explore(find=addr_correct, avoid=addr_avoid, num_find=1)
    except Exception as e:
        log.error("Exploration error: %s", e)

    log.info("active=%d found=%d avoid=%d deadended=%d",
             len(sm.active), len(sm.found), len(sm.avoid), len(sm.deadended))

    if sm.found:
        found = sm.found[0]
        log.info("SOLUTION FOUND!")
        try:
            flag_bytes = found.posix.dumps(0)
            flag = flag_bytes.rstrip(b'\n\x00').decode('latin-1', errors='replace')
            log.info("Flag: %s", flag)
            print(f"\n{'='*60}")
            print(f"FLAG: {flag}")
            print(f"{'='*60}\n")
            return flag
        except Exception as e:
            log.error("Extraction: %s", e)

    return None

if __name__ == '__main__':
    result = main()
    sys.exit(0 if result else 1)
