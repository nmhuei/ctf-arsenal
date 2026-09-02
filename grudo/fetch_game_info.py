import asyncio, json
from playwright.async_api import async_playwright

URLS = [
    '/api/game/2',
    '/api/game/2/scoreboard',
    '/api/game/2/scoreboardsheet',
]

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
        context=await browser.new_context(storage_state='state70.json')
        page=await context.new_page()
        await page.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
        for url in URLS:
            res=await page.evaluate("""async (url)=>{const r=await fetch(url,{credentials:'include'});return {status:r.status,type:r.headers.get('content-type'),text:await r.text()}}""",url)
            print('URL',url,'STATUS',res['status'],'TYPE',res['type'])
            try: print(json.dumps(json.loads(res['text']),ensure_ascii=False,indent=2)[:20000])
            except: print(res['text'][:1000])
        await browser.close()
asyncio.run(main())
