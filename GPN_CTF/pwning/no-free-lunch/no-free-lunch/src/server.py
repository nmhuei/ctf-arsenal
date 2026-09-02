import tempfile
import os


def main() -> None:
    py: str = ""
    print('Send your input line by line. End input with the text "EOF":\n')
    while True:
        try:
            line = input()
        except EOFError:
            print("Unexpected EOF, exiting...", flush=True)
            return
        if line.strip() == "EOF":
            break
        py += line + "\n"

    if len(py) >= 100_000:
        print("Too long input", flush=True)
        return

    with tempfile.NamedTemporaryFile(suffix=".py") as f:
        f.write(b"""import heapq # the only import you'll need today
from sys import addaudithook
from os import _exit
addaudithook(lambda x,y:_exit(0))
""")
        f.write(py.encode())
        f.seek(0)

        try:
            print("Starting Jail...", flush=True)
            os.execve(
                "./python",
                [
                    "python",
                    f.name,
                ],
                {"PYTHONPATH": "./lib/"},
            )
        except Exception as e:
            print(e, flush=True)


if __name__ == "__main__":
    main()
