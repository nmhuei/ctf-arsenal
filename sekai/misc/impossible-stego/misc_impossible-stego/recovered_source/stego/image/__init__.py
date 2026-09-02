"""Image-side machinery: carrier model, slot scatter and matched LSB embedding."""

from .carrier import Carrier
from .scatter import slot_order
from .embed import embed_bits, extract_bits

__all__ = ["Carrier", "slot_order", "embed_bits", "extract_bits"]
