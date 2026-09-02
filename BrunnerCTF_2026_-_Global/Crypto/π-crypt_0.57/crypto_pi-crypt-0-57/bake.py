from secret import flag, key

# Company policy mandates that all keys must be a 64-character sentence in plain text
# Symbols are encouraged for added security... but spaces must be swapped with underscores...
assert len(key) == 64

# The new π-crypt 0.57 is still based on last season's vanilla version of π-crypt:
base = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789æøåÆØÅ .,!?-:()[]/{}=<>+_@^|~%$#&*`“';"
assert all(c in base for c in flag + key) and flag[:8] + flag[-1] == "brunner{}"

with open("unbaked_pi.txt") as f:
    pie = f.read()

assert len(base) == 100 and len(pie) == 1000


def pie_crypt(text: str, key: str, decrypt: bool = False) -> str:
    out = ""
    i = sum(base.index(c) for c in key)
    j = 0

    for c in text:
        d1 = int(pie[i % len(pie)])
        i += base.index(key[j % len(key)])
        j += 1

        d2 = int(pie[i % len(pie)])
        i += base.index(key[j % len(key)])
        j += 1

        shift = 10 * d1 + d2
        out += base[(base.index(c) + (-shift if decrypt else shift)) % len(base)]

    return out


# But it takes it to a new level by adding in a modified version of a
# Feistel network implementation for additional security:

def custom_ingredient(
    text: str, key: str, decrypt: bool = False, rounds: int = 16
) -> str:
    if decrypt:
        previous_left, previous_right, left, right = [
            text[i * (n := len(text) // 4) : (i + 1) * n] for i in range(4)
        ]
    else:
        left, right = text[: len(text) // 2], text[len(text) // 2 :]
        previous_left, previous_right = "A" * len(left), "A" * len(right)
    assert all(len(s) == len(key) for s in [previous_left, previous_right, left, right])

    def custom_xor(s1, s2, decrypt=False):
        return "".join(
            base[(base.index(c1) + base.index(c2) * (-1 if decrypt else 1)) % len(base)]
            for c1, c2 in zip(s1, s2)
        )

    def round_function(previous_left, previous_right, left, right):
        if decrypt:
            new_right = left
            new_left = custom_xor(right, custom_xor(new_right, key), True)
            return new_left, new_right, previous_left, previous_right
        else:
            new_left = previous_right
            new_right = custom_xor(previous_left, custom_xor(previous_right, key))
            return left, right, new_left, new_right

    extra_rounds = rounds - 1
    for _ in range(extra_rounds):
        (previous_left, previous_right, left, right) = round_function(
            previous_left, previous_right, left, right
        )

    return "".join(round_function(previous_left, previous_right, left, right))


# Finally, we are ready to bake:

def main(decrypt: bool = False):
    if decrypt:
        with open("baked_pie.txt", "r", encoding="utf-8") as f:
            text = f.read()
        left, right = (
            (t := custom_ingredient(text, key, decrypt))[2 * (n := len(t) // 4) : 3 * n],
            t[3 * n :],
        )
        text = pie_crypt(left + right, key, decrypt)
        print(text)
    else:
        text = flag
        text = pie_crypt(text, key)
        text = custom_ingredient(text, key)
        with open("baked_pie.txt", "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
