"""Execute one program after applying the n8n-compatible Python guards."""

import sys


def main():
    source = sys.stdin.read()
    compiled = compile_user_code(source)

    sanitize_sys_modules()
    harden_importlib()
    namespace = {
        "__builtins__": safe_builtins(),
        SAFE_FORMAT_KEY: SAFE_FORMAT,
    }
    exec(compiled, namespace, namespace)


try:
    main()
except SecurityViolationError as error:
    print(f"SecurityViolationError: {error}", file=sys.stderr)
    if error.description:
        print(error.description, file=sys.stderr)
    sys.exit(1)
