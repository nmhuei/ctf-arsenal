#!/usr/bin/env python3
"""
angr solver for r3fake/lift challenge - v5 (Debug/Step-through).

Debug version: step through instructions to see how far we get.
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

    # Hook strncmp
    strncmp_addr = base + 0x1040
    log.info("strncmp@plt at 0x%x", strncmp_addr)

    # Hook setrlimit/getrlimit/printf/fflush
    proj.hook(base + 0x10c0, angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())
    proj.hook(base + 0x10e0, angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())

    # Create state at main function start, skip fgets by directly setting buffer
    addr_start = base + 0x21ebcf  # main

    STACK_BASE = 0x7fffffffffeff00
    state = proj.factory.blank_state(
        addr=addr_start,
        add_options={
            angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
            angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
            angr.options.OPTIMIZE_IR,
        },
    )

    # Set up stack for main
    # Main prologue: push rbp; mov rbp, rsp; sub rsp, 0x240
    # Before main starts: rsp should be valid
    state.regs.rsp = STACK_BASE
    state.regs.rbp = STACK_BASE

    # Main expects argc/argv/envp
    state.regs.rdi = 1  # argc
    state.regs.rsi = STACK_BASE + 0x1000  # argv
    state.regs.rdx = 0  # envp

    # Create the input buffer BEFORE main starts
    # We'll write it after the prologue executes
    # Actually, let's just let main run and see what happens

    log.info("=== Starting execution from main ===")
    sm = proj.factory.simulation_manager(state)

    # Step manually
    step_count = 0
    max_steps = 5000
    start_time = time.time()

    while step_count < max_steps:
        sm.step()
        step_count += 1

        if step_count % 500 == 0:
            log.info("Step %d: active=%d deadended=%d", step_count, len(sm.active), len(sm.deadended))

        if len(sm.active) == 0:
            log.info("No more active states after %d steps", step_count)
            break

    elapsed = time.time() - start_time
    log.info("Ran %d steps in %.1fs (%.0f steps/s)", step_count, elapsed, step_count/elapsed)
    log.info("active=%d deadended=%d", len(sm.active), len(sm.deadended))

    # Log active state address if any
    for i, s in enumerate(sm.active[:5]):
        log.info("Active[%d] addr=0x%x constraints=%d", i, s.addr, len(s.solver.constraints))

    if sm.deadended:
        log.info("Deadended[0] addr=0x%x", sm.deadended[0].addr)

    return None

if __name__ == '__main__':
    main()
