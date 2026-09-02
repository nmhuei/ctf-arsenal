import requests
import base64
import re

def solve():
    base_url = "https://11be9059-6c6b-499c-94b8-ae09a8dc6ed9.222.255.138.122.nip.io"
    
    # 1. Access arXiv paper
    print("[*] Fetching arXiv paper...")
    r_arxiv = requests.get(f"{base_url}/arxiv/abs/2605.99847", verify=False)
    
    # 2. Access X profile
    print("[*] Fetching X profile...")
    r_x = requests.get(f"{base_url}/x/khoa_neuralnet", verify=False)
    
    # 3. Access GitHub repo
    print("[*] Fetching GitHub repo...")
    r_gh = requests.get(f"{base_url}/gh/minhkhoa-ai/phantom-gradient-descent", verify=False)
    
    # 4. Access Pastebin notes
    print("[*] Fetching Pastebin notes...")
    r_paste = requests.get(f"{base_url}/p/gg5oggvj", verify=False)
    
    # 5. Extract master_key_b64
    m = re.search(r'master_key_b64\s*=\s*"([^"]+)"', r_paste.text)
    if m:
        b64_key = m.group(1)
        flag = base64.b64decode(b64_key).decode("utf-8")
        print(f"[+] Found Flag: {flag}")
        return flag
    else:
        print("[-] Flag not found in paste.")
        return None

if __name__ == "__main__":
    solve()
