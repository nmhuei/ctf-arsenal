"""
stego — layered, source-only steganography.

All security resides in this source tree: there is no passphrase.  See
pipeline.py for the full transform stack.
"""

from .pipeline import embed, extract, StegoError

__all__ = ["embed", "extract", "StegoError"]
__version__ = "2.0"
