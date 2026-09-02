import os

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

QRSCAN_DIR = os.environ.get("QRSCAN_DIR", "/run/chal")
QRSCAN = os.environ.get("QRSCAN", "./qrscan")
QRSCAN_LOADER = os.environ.get("QRSCAN_LOADER", "/run/chal/ld-linux-x86-64.so.2")
QRSCAN_ARGV = [QRSCAN_LOADER, "--library-path", QRSCAN_DIR, QRSCAN]
DECODER_TIMEOUT = 90

MAX_DIMENSION = 0x7fffffff
MAX_PIXELS = 5 * 1024 * 1024 * 1024
