"""
Command-line interface.

    python3 -m stego embed   <in.png> <out.png> "secret text"
    python3 -m stego embed   <in.png> <out.png> --infile message.bin
    python3 -m stego extract <stego.png>
    python3 -m stego extract <stego.png> --out recovered.bin
"""

import argparse
import sys

from . import embed, extract, StegoError


def main(argv=None):
    parser = argparse.ArgumentParser(prog="stego", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("embed", help="hide a message in an image")
    pe.add_argument("input")
    pe.add_argument("output")
    pe.add_argument("message", nargs="?", help="text to hide (UTF-8)")
    pe.add_argument("--infile", help="read raw message bytes from this file")

    px = sub.add_parser("extract", help="recover a hidden message")
    px.add_argument("input")
    px.add_argument("--out", help="write recovered bytes to this file")

    args = parser.parse_args(argv)

    if args.cmd == "embed":
        if args.infile:
            with open(args.infile, "rb") as fh:
                msg = fh.read()
        elif args.message is not None:
            msg = args.message.encode("utf-8")
        else:
            parser.error("provide a message argument or --infile")
        try:
            embed(args.input, args.output, msg)
        except StegoError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Embedded {len(msg)} bytes -> {args.output}")
        return 0

    if args.cmd == "extract":
        try:
            data = extract(args.input)
        except StegoError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.out:
            with open(args.out, "wb") as fh:
                fh.write(data)
            print(f"Recovered {len(data)} bytes -> {args.out}")
        else:
            sys.stdout.buffer.write(data)
            if sys.stdout.isatty():
                sys.stdout.write("\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
