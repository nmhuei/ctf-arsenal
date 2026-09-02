import requests

url = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf/test/7f9c18a2e44d/fe291443882d55af94bff1f9cddffb73.pcap"
r = requests.get(url)
print(f"Status: {r.status_code}, Length: {len(r.content)} bytes")
if r.status_code == 200:
    with open("ghost_zero.pcap", "wb") as f:
        f.write(r.content)
    print("Saved to ghost_zero.pcap")
