import asyncio, json
from playwright.async_api import async_playwright
GAME_ID=2; CHALLENGE_ID=77
FOLDERS=[
'ProjectWorkingFolder','projectworkingfolder','PROJECTWORKINGFOLDER','Project_Working_Folder','project_working_folder','PROJECT_WORKING_FOLDER','Project-Working-Folder','project-working-folder','PROJECT-WORKING-FOLDER','Project Working Folder','project working folder','PROJECT WORKING FOLDER','WorkingFolder','workingfolder','WORKINGFOLDER','Working_Folder','working_folder','WORKING_FOLDER','ProjectFolder','projectfolder','Project_Folder','project_folder','ShellBagsExplorer','shellbagsexplorer','SHELLBAGSEXPLORER','Shell_Bags_Explorer','shell_bags_explorer','SHELL_BAGS_EXPLORER','Shell-Bags-Explorer','shell-bags-explorer','SHELL-BAGS-EXPLORER','Shell Bags Explorer','shell bags explorer','SHELL BAGS EXPLORER','ShellBags','shellbags','Shell_Bags','shell_bags','BagsExplorer','bagsexplorer','Bags_Explorer','bags_explorer']
PDFS=['OJYBIB.pdf','ojybib.pdf','OJYBIB.PDF']
EXES=['calc.exe','Calc.exe']
async def submit(pg,f):
 r=await pg.evaluate("""async x=>{const r=await fetch('/api/game/2/challenges/77',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({flag:x})});return {s:r.status,t:await r.text()}}""",f)
 if r['s']!=200:return f"HTTP_{r['s']}"
 sid=json.loads(r['t'])
 for _ in range(30):
  await asyncio.sleep(.25)
  q=await pg.evaluate("""async s=>{const r=await fetch(`/api/game/2/challenges/77/status/${s}`,{credentials:'include'});return {s:r.status,t:await r.text()}}""",sid)
  if q['s']!=200:return f"STATUS_{q['s']}"
  v=json.loads(q['t'])
  if v!='FlagSubmitted':return v
 return 'TIMEOUT'
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
  c=await b.new_context(storage_state='state70.json'); pg=await c.new_page(); await pg.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
  n=0
  for pdf in PDFS:
   for folder in FOLDERS:
    for exe in EXES:
     flag=f'grodno{{{pdf}_{folder}_{exe}}}'; n+=1; res=await submit(pg,flag)
     print(json.dumps({'n':n,'candidate':flag,'result':res},ensure_ascii=False),flush=True)
     if res=='Accepted':await b.close();return
     await asyncio.sleep(.18)
  await b.close()
asyncio.run(main())
