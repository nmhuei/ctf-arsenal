#!/usr/bin/env python3
"""
angr concrete tracer for r3fake/lift.

Run the binary with concrete input and trace execution paths.
Hooks all important functions to understand the validation flow.
"""

import angr
import claripy
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger(__name__)

BINARY_PATH = '/home/light/Workspace/CTF/r3fake/lift/chall'
FLAG_LEN = 39
CONTENT_LEN = 32

# Log every step
class Tracer:
    def __init__(self, proj, base, test_input):
        self.proj = proj
        self.base = base
        self.test_input = test_input
        self.steps = 0
        self.max_steps = 20000
        self.strncmp_count = 0

    def trace(self):
        """Run with concrete input and trace execution."""
        # Create state at main
        addr_main = self.base + 0x21ebcf

        STACK_BASE = 0x7fffffffffeff00
        state = self.proj.factory.blank_state(
            addr=addr_main,
            add_options={
                angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
                angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
            },
        )

        state.regs.rsp = STACK_BASE
        state.regs.rbp = STACK_BASE
        state.regs.rdi = 1  # argc
        state.regs.rsi = 0  # argv
        state.regs.rdx = 0  # envp

        # Set up stdin with test input
        test_data = self.test_input + b'\n'
        state.posix.files[0] = angr.storage.file.SimFile('/dev/stdin', content=test_data)
        state.posix.files[0].has_end = True

        # Hook setrlimit/getrlimit
        self.proj.hook(self.base + 0x10c0, angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())
        self.proj.hook(self.base + 0x10e0, angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())

        sm = self.proj.factory.simulation_manager(state)

        # Step concretely
        self.steps = 0
        while self.steps < self.max_steps:
            sm.step()
            self.steps += 1

            # Log key events
            for s in sm.active:
                if s.addr > 0x400000:
                    # Check if we're in interesting areas
                    offset = s.addr - self.base
                    if 0x214326 <= offset <= 0x214500:
                        log.info("IN VALIDATION FUNC (offset 0x%x)", offset)
                    elif offset == 0x21eb44:
                        log.info("*** HIT CORRECT! FUNCTION ***")
                    elif offset == 0x21eb6d:
                        log.info("*** HIT FAIL... FUNCTION ***")

            if self.steps % 1000 == 0:
                log.info("Step %d: active=%d deadended=%d", self.steps, len(sm.active), len(sm.deadended))

            if len(sm.active) == 0:
                log.info("No more active states after %d steps", self.steps)
                break

        log.info("Tracing complete: %d steps", self.steps)
        log.info("Active: %d, Deadended: %d", len(sm.active), len(sm.deadended))

        for i, s in enumerate(sm.active[:3]):
            log.info("Active[%d]: offset=0x%x", i, s.addr - self.base)

        return sm


def main():
    log.info("Loading binary: %s", BINARY_PATH)
    proj = angr.Project(BINARY_PATH, auto_load_libs=False)
    base = proj.loader.main_object.mapped_base
    log.info("PIE base: 0x%x", base)

    # Test input: "R3CTF{" + 32 'A's + "}"
    test_input = b"R3CTF{" + b"A" * 32 + b"}"

    tracer = Tracer(proj, base, test_input)
    tracer.trace()

    return 0

if __name__ == '__main__':
    sys.exit(main())
