
import sys
def idk(a, b, fn):
    fn(a, b)
code = ''.join(c for c in open("user_input").read() if c in "abcdefghijklmnopqrstuvwxyz:_.[],")
if "ass" in code or "typ" in code or "als" in code:
    print("Nope")
else:
    eval(code, {"__builtins__": {"idk":idk,"sys":sys}})
