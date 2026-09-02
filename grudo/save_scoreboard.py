import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
        context=await browser.new_context(storage_state='state70.json')
        page=await context.new_page()
        await page.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
        res=await page.evaluate("""async()=>{const r=await fetch('/api/game/2/scoreboard',{credentials:'include'});return {status:r.status,text:await r.text()}}""")
        print('STATUS',res['status'])
        open('scoreboard_full.json','w',encoding='utf-8').write(res['text'])
        obj=json.loads(res['text'])
        print('KEYS',obj.keys())
        def walk(x,path=''):
            if isinstance(x,dict):
                for k,v in x.items():
                    if str(k).lower().find('challenge')>=0 or str(k).lower().find('blood')>=0 or str(k).lower().find('solve')>=0:
                        print('FIELD',path+'/'+str(k),type(v).__name__,str(v)[:500])
                    walk(v,path+'/'+str(k))
            elif isinstance(x,list):
                for i,v in enumerate(x): walk(v,path+f'/{i}')
        walk(obj)
        await browser.close()
asyncio.run(main())
