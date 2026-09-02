import asyncio, json
from playwright.async_api import async_playwright

GAME_ID=2
CHALLENGE_ID=77
FOLDERS=[
    'ProjectWorkingFolder','projectworkingfolder','PROJECTWORKINGFOLDER',
    'Project_Working_Folder','project_working_folder','PROJECT_WORKING_FOLDER',
    'Project-Working-Folder','project-working-folder','PROJECT-WORKING-FOLDER',
    'Project Working Folder','project working folder','PROJECT WORKING FOLDER',
    'WorkingFolder','workingfolder','WORKINGFOLDER',
    'Working_Folder','working_folder','WORKING_FOLDER',
    'ProjectFolder','projectfolder','Project_Folder','project_folder',
    'ShellBagsExplorer','shellbagsexplorer','SHELLBAGSEXPLORER',
    'Shell_Bags_Explorer','shell_bags_explorer','SHELL_BAGS_EXPLORER',
    'Shell-Bags-Explorer','shell-bags-explorer','SHELL-BAGS-EXPLORER',
    'Shell Bags Explorer','shell bags explorer','SHELL BAGS EXPLORER',
    'ShellBags','shellbags','Shell_Bags','shell_bags',
    'BagsExplorer','bagsexplorer','Bags_Explorer','bags_explorer',
]

async def submit(page,candidate):
    r=await page.evaluate("""async ({g,c,f})=>{const r=await fetch(`/api/game/${g}/challenges/${c}`,{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({flag:f})});return {status:r.status,text:await r.text()}}""",{'g':GAME_ID,'c':CHALLENGE_ID,'f':candidate})
    if r['status']!=200:return f"HTTP_{r['status']}:{r['text'][:100]}"
    sid=json.loads(r['text'])
    for _ in range(30):
        await asyncio.sleep(.3)
        s=await page.evaluate("""async ({g,c,s})=>{const r=await fetch(`/api/game/${g}/challenges/${c}/status/${s}`,{credentials:'include'});return {status:r.status,text:await r.text()}}""",{'g':GAME_ID,'c':CHALLENGE_ID,'s':sid})
        if s['status']!=200:return f"STATUS_HTTP_{s['status']}"
        v=json.loads(s['text'])
        if v!='FlagSubmitted':return v
    return 'TIMEOUT'

async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
  c=await b.new_context(storage_state='state70.json'); pg=await c.new_page()
  await pg.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
  for i,folder in enumerate(FOLDERS,1):
   flag=f'grodno{{OJYBIB.pdf_{folder}_CALC.EXE}}'
   result=await submit(pg,flag)
   print(json.dumps({'n':i,'candidate':flag,'result':result},ensure_ascii=False),flush=True)
   if result=='Accepted':break
   await asyncio.sleep(.25)
  await b.close()
asyncio.run(main())
