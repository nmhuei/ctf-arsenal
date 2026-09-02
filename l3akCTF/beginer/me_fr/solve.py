text = """Jo! Sp O was tjomlomg/// tu[omg os kist sp jard mpwadaus! :pplomg at upir jamds wjo;e upi tu[e os omfiroatomg. Amuwaus. jeres tje f;ag" :3AL}WJU+D-+1+dP+TJ1S+s-+-f83M///|"""

mapping = {
    "u": "y",
    "i": "u",
    "o": "i",
    "p": "o",
    "[": "p",

    "j": "h",
    "k": "j",
    "l": "k",
    ";": "l",
    ":": "L",

    "m": "n",

    "-": "0",
    "+": "_",
    "8": "7",
    "/": ".",
    "|": "}",
    "}": "{",
}

# tạo map phụ để dùng chung in hoa / in thường
mapping_lower = {
    k.lower(): v
    for k, v in mapping.items()
}

result = ""

for c in text:
    key = c.lower()

    if key in mapping_lower:
        new = mapping_lower[key]

        if c.isupper():
            result += new.upper()
        elif c.islower():
            result += new.lower()
        else:
            result += new
    else:
        result += c

print(result)
