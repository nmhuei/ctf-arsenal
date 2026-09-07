#!/usr/bin/env python3
# leftover from debugging, ignore this

import base64

FLAG_thbby = "ZGVmaW5pdGVseV9ub3RfZ3JvZG5vezd2N3JiYWxycDh9"

def check_zvday():
    return base64.b64decode(FLAG_thbby).decode()

if __name__ == "__main__":
    print(check_zvday())
