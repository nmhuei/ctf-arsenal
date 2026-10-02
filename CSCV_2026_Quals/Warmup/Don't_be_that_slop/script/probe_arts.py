import json, glob, os
base = os.path.dirname(os.path.abspath(__file__)) + "/articles"
for f in sorted(glob.glob(base + "/*.json")):
    d = json.load(open(f))
    c = d.get("content", "")
    if ("\\" in c or "$" in c or "flag" in c.lower() or "cscv" in c.lower()
            or "latex" in c.lower() or "pandoc" in c.lower()):
        print("===", os.path.basename(f), "|", d.get("title"))
        print(c[:1200])
        print()
