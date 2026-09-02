import struct

import png

from .config import MAX_DIMENSION, MAX_PIXELS

HEADER = struct.Struct("<II")
ERROR = "The uploaded ticket could not be read."


def write_image(stream, out):
    try:
        stream.seek(0)
        count = 0

        for width, height, rows in iter(lambda: read_png(stream), None):
            count += 1
            write_frame(out, width, height, rows)

        if not count:
            raise ValueError(ERROR)
    except Exception as exc:
        raise ValueError(ERROR) from exc


def read_png(stream):
    if not has_data(stream):
        return None
    width, height, rows, info = png.Reader(file=stream).asDirect()
    if (
        not info.get("greyscale")
        or info.get("alpha")
        or info.get("bitdepth") != 8
        or not (0 < width <= MAX_DIMENSION)
        or not (0 < height <= MAX_DIMENSION)
        or width * height > MAX_PIXELS
    ):
        raise ValueError(ERROR)
    return width, height, rows


def has_data(stream):
    start = stream.tell()
    data = stream.read(1)
    stream.seek(start)
    return bool(data)


def write_frame(out, width, height, rows):
    out.write(HEADER.pack(width, height))
    start = out.tell()
    zero_row = b"\0" * width
    count = 0

    for row in rows:
        row = bytes(row)
        if len(row) != width:
            raise ValueError(ERROR)
        if row != zero_row:
            out.seek(start + count * width)
            out.write(row)
        count += 1

    if count != height:
        raise ValueError(ERROR)

    out.seek(start + width * height)
    out.truncate(out.tell())
