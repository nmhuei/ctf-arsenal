#!/usr/bin/env python3
import socket
import sys
import time

def auto_answer(question_text):
    q = question_text.lower()
    if "tên tài khoản" in q or "người gửi" in q:
        return "ptitctf2026.chall.for, longhd05"
    elif "hẹn gặp" in q or "ở đâu" in q or "địa điểm" in q:
        return "Học Viện Công Nghệ Bưu Chính Viễn Thông - PTIT"
    elif "mật khẩu mở phòng" in q or "phòng" in q:
        return "9322.5"
    elif "hotspot" in q or "điểm phát" in q or "mật khẩu wifi" in q:
        return "3jvk2s7tubjwhzp"
    elif "tên wifi" in q or "ssid" in q:
        return "Forensics"
    elif "email" in q or "gmail" in q:
        return "nonnongaga12345@gmail.com"
    elif "ảnh" in q or "tên file" in q or "hình ảnh" in q:
        return "IMG_3963.jpg"
    return None

def solve(host, port):
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    try:
        s.connect((host, int(port)))
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return

    buffer = ""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            text = chunk.decode("utf-8", errors="ignore")
            print(text, end="", flush=True)
            buffer += text

            if "> " in buffer:
                # Find the current question
                lines = buffer.strip().split("\n")
                last_prompt = lines[-1]
                ans = auto_answer(buffer)
                if ans:
                    print(f"[+] Suggested answer: {ans}")
                    # Allow quick enter or auto send
                    s.sendall(ans.encode("utf-8") + b"\n")
                else:
                    ans = input("\n[?] Enter answer: ")
                    s.sendall(ans.encode("utf-8") + b"\n")
                buffer = ""
            
            if "FLAG{" in buffer or "flag{" in buffer:
                print("\n[🎉] Found flag!")
                break
        except socket.timeout:
            print("\n[-] Socket timeout.")
            break
        except KeyboardInterrupt:
            print("\n[-] Interrupted by user.")
            break

    s.close()

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else "144.79.188.39"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 45119
    solve(host, port)
