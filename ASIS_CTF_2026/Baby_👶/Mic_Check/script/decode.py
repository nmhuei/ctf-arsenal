#!/usr/bin/env python3
"""
Probe and parser for Mic Check (Baby 👶) - ASIS CTF Quals 2026.
Decodes hand-drawn vintage LED 7-segment / 14-segment ASCII readouts.
"""

BLOCKS = [
    # [1]
    (
        " _       _   _       _        \n"
        "|_  |_| |_|  _| | |  _| |  |  \n"
        "|     | |\\   _| |/|  _| |_ |_ "
    ),
    # [2]
    (
        " _       _   _   _     \n"
        "|   |   |_| |_  |_   | |  \n"
        "|_  |_    |  _|  _|  | |_ "
    ),
    # [3]
    (
        "     _            _  \n"
        "|_|  _| |   |   | | \n"
        "| |  _| |_  |_  |_| "
    ),
    # [4] Note: drifted top row in ASCII rendering
    (
        "     _   _   _   _  _|_      _ \n"
        "| | | | |    _| |_|  |  |_| | | |\n"
        "|_| | | |_   _| |\\   |    | | | |"
    ),
    # [5]
    (
        " _   _        \n"
        " _| |_| |_| | \n"
        " _| |\\    | ."
    )
]

# Manual decoded mapping of the blocks
DECODED_BLOCKS = [
    "f4r3w3ll",
    "cl4ss1c",
    "h3ll0",
    "unc3rt41n",
    "3r4!"
]

def main():
    print("[*] Decoding Mic Check ASCII blocks...")
    for idx, (b, decoded) in enumerate(zip(BLOCKS, DECODED_BLOCKS), 1):
        print(f"--- Block [{idx}] ---")
        print(b)
        print(f"Decoded: {decoded}\n")

    flag = f"ASIS{'{'}{'_'.join(DECODED_BLOCKS)}{'}'}"
    print(f"[+] Reconstructed Flag: {flag}")

if __name__ == "__main__":
    main()
