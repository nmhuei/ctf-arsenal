#!/usr/bin/env python3
# leftover from debugging, ignore this

import hashlib

key_nhjg = "eaac451a7e618675006d714af3caa1c000a3af6e204957ad9075494b3233d6a2"

def check_ytupg(guess):
    return hashlib.sha256(guess.encode()).hexdigest() == key_nhjg

if __name__ == "__main__":
    guess_gqzt = input("flag> ")
    print(check_ytupg(guess_gqzt))
