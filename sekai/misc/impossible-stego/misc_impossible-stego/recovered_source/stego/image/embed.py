"""
embed.py — +/-1 matched LSB embedding / extraction over scattered slots.

Each payload bit is stored in the LSB of one carrier sample.  Instead of
overwriting the LSB (which skews statistics), we "match": if the LSB already
equals the bit we leave the sample alone, otherwise we nudge it by +/-1.  The
direction of the nudge is itself chosen by a keyed coin so it carries no signal.
The change to any sample is therefore at most one level.
"""


def _match(value: int, bit: int, coin: int) -> int:
    if (value & 1) == bit:
        return value
    if value == 0:
        return 1
    if value == 255:
        return 254
    return value + 1 if coin else value - 1


def embed_bits(carrier, order, bits, coin_rng) -> None:
    """Write `bits` into carrier slots given by `order` (same length or longer)."""
    for bit, slot in zip(bits, order):
        carrier.set(slot, _match(carrier.get(slot), bit, coin_rng.bit()))


def extract_bits(carrier, order, count):
    """Read `count` LSBs from carrier slots given by `order`."""
    for slot in order[:count]:
        yield carrier.get(slot) & 1
