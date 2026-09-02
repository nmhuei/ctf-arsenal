"""
carrier.py — flat, mutable view over an image's RGB carrier channels.

Wraps a Pillow image as a flat list of R,G,B samples (alpha kept aside and
never modified).  Slot index `s` maps to pixel `s // 3`, channel `s % 3`.
"""

from PIL import Image

from .. import secret


class Carrier:
    def __init__(self, path: str):
        img = Image.open(path).convert("RGBA")
        self.width, self.height = img.size
        self.channels = secret.CARRIER_CHANNELS
        pixels = list(img.getdata())  # list of (r,g,b,a)
        # Separate carrier samples from the untouched alpha plane.
        self._samples = bytearray(self.width * self.height * self.channels)
        self._alpha = bytearray(self.width * self.height)
        for i, (r, g, b, a) in enumerate(pixels):
            base = i * self.channels
            self._samples[base] = r
            self._samples[base + 1] = g
            self._samples[base + 2] = b
            self._alpha[i] = a

    @property
    def capacity_bits(self) -> int:
        return len(self._samples)

    def get(self, slot: int) -> int:
        return self._samples[slot]

    def set(self, slot: int, value: int) -> None:
        self._samples[slot] = value & 0xFF

    def save(self, path: str) -> None:
        out = []
        s = self._samples
        for i in range(self.width * self.height):
            base = i * self.channels
            out.append((s[base], s[base + 1], s[base + 2], self._alpha[i]))
        img = Image.new("RGBA", (self.width, self.height))
        img.putdata(out)
        img.save(path, "PNG")
