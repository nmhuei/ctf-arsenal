import subprocess

cmd = ["tshark", "-r", "ghost_zero.pcap", "-V"]
out = subprocess.check_output(cmd).decode('utf-8', errors='ignore')

# Extract HTTP request/response lines
lines = out.split('\n')
for i, line in enumerate(lines):
    if "Hypertext Transfer Protocol" in line or "HTTP/1." in line or "POST " in line or "GET " in line:
        print("\n".join(lines[i:i+40]))
        print("="*60)
