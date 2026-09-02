import asyncio, json
from playwright.async_api import async_playwright

TEAM_IDS=[538,712,421,86,889,400]
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
  c=await b.new_context(storage_state='state70.json'); pg=await c.new_page()
  await pg.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
  for tid in TEAM_IDS:
   r=await pg.evaluate("""async id=>{const r=await fetch(`/api/team/${id}`,{credentials:'include'});return {status:r.status,text:await r.text()}}""",tid)
   print('TEAM',tid,'STATUS',r['status'])
   try: print(json.dumps(json.loads(r['text']),ensure_ascii=False,indent=2))
   except: print(r['text'][:1000])
  await b.close()
asyncio.run(main())
