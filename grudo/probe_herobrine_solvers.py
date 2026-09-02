import asyncio, json
from playwright.async_api import async_playwright

URLS = [
    '/api/game/2/scoreboard',
    '/api/game/2/teams/13', '/api/game/2/team/13', '/api/team/13', '/api/teams/13',
    '/api/game/2/teams/21', '/api/game/2/team/21', '/api/team/21', '/api/teams/21',
    '/api/game/2/teams/108', '/api/game/2/team/108', '/api/team/108', '/api/teams/108',
    '/api/game/2/challenges/90/solves', '/api/game/2/challenges/90/submissions',
]

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
    ctx=await browser.new_context(storage_state='state70.json')
    page=await ctx.new_page()
    await page.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
    for url in URLS:
      r=await page.evaluate("""async u=>{let r=await fetch(u,{credentials:'include'});return {status:r.status,ct:r.headers.get('content-type'),text:await r.text()}}""",url)
      print('\n###',url,r['status'],r['ct'])
      print(r['text'][:5000])
    await browser.close()

asyncio.run(main())
