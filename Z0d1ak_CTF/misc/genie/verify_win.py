#!/usr/bin/env python3
"""Replay the genie winning movie in PyBoy with the seed at c0f0/c0f1
(the location the ROM's K-derivation reads at 0x0e81) and verify the WIN state."""
import sys
sys.path.insert(0, '/home/light/GitHub/gpt/scratch/ctf-workspaces/genie/venv/lib/python3.13/site-packages')
from pyboy import PyBoy

ROM = '/home/light/GitHub/gpt/scratch/ctf-workspaces/genie/seal.gb'
MASK16 = 0xFFFF

def rol16(x, n):
    x &= MASK16
    return ((x << n) | (x >> (16 - n))) & MASK16

def seed_key(seed):
    return ((0x3D29 + rol16(seed ^ 0xA5C3, 7)) & MASK16) ^ 0x6B71

def gold_mac(gold, key):
    mixed = (0x6D2B + rol16(gold ^ key, 3)) & MASK16
    return rol16(mixed ^ rol16(key, 7), 5)

def codewords(seed, gold=5000):
    k = seed_key(seed)
    return gold, gold ^ k, gold_mac(gold, k)

def rd16(p, a):
    return p.memory[a] | (p.memory[a + 1] << 8)

SEED = 2530
w0, w1, w2 = codewords(SEED)
print(f"seed={SEED}: K=0x{seed_key(SEED):04X} C100=0x{w0:04X} C102=0x{w1:04X} C104=0x{w2:04X}")

pyboy = PyBoy(ROM, window='null')
# The ROM reads the session seed from c0f0:c0f1 during setup (0x0e81), and
# never writes it itself -- the service pre-seeds that RAM window.
pyboy.memory[0xC0F0] = SEED & 0xFF
pyboy.memory[0xC0F1] = (SEED >> 8) & 0xFF

# Winning movie (writeup layout):
#   frame 20: write C100/C102/C104 (authenticated gold=5000), press START
#   frames 40..136: A presses, selector write on the following frame
ECHO = [2, 0, 2, 1, 2, 2, 0, 2, 1]
TOTAL = 220
joypad_events = {20: 'start'}
codes = {20: [(0xC100, w0), (0xC102, w1), (0xC104, w2)]}
frame = 41
for sel in ECHO:
    codes[frame] = [(0xC300, sel)]
    frame += 12
for f in (40, 52, 64, 76, 88, 100, 112, 124, 136):
    joypad_events[f] = 'a'

pressed = False
for f in range(TOTAL):
    for addr, val in codes.get(f, []):
        pyboy.memory[addr] = val & 0xFF
        pyboy.memory[addr + 1] = (val >> 8) & 0xFF
    ev = joypad_events.get(f)
    if ev:
        pyboy.button(ev)
        pressed = True
    elif pressed:
        pyboy.button_release('right')
        pressed = False
    pyboy.tick()

gold = rd16(pyboy, 0xC100)
gx = rd16(pyboy, 0xC102)
gmac = rd16(pyboy, 0xC104)
floor = pyboy.memory[0xC406]
sub = pyboy.memory[0xC407]
state = rd16(pyboy, 0xC200)
hashw = rd16(pyboy, 0xC202)
echo_n = pyboy.memory[0xC412]
print(f"floor={floor} sub={sub:02x} gold={gold} state=0x{state:04X} hash=0x{hashw:04X} echoes={echo_n}")
print(f"gold tuple: C100={gold} C102=0x{gx:04X} C104=0x{gmac:04X}")
print(f"target hash = 0xB14A -> {'WIN!' if hashw == 0xB14A else 'not yet'}")
print(f"c0f0={pyboy.memory[0xC0F0]:02X}{pyboy.memory[0xC0F1]:02X}")
print(f"c400 backup = {[hex(pyboy.memory[a]) for a in range(0xC400, 0xC406)]}")
pyboy.stop()
