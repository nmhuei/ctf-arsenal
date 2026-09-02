import asyncio
import json
from playwright.async_api import async_playwright

GAME_ID = 2
CHALLENGE_ID = 77
PDFS = [
    "osTriageManual.pdf",
    "invoice_4-141025-5909.pdf",
    "invoice_4-140825-6359.pdf",
    "INV00818612.pdf",
    "GOON2Manual.pdf",
    "QuickStartGuide_SanDiskSecureAccessV2.0.pdf",
    "FTKManual.pdf",
    "251.pdf",
    "Smart insite.pdf",
    "ATA-7 Spec Vol3 Rev4a.pdf",
    "SCSI Primary Commands 2-T10 Group-r20.pdf",
    "SCSI Multimedia Commands mmc4r03.pdf",
    "OutlookFolders.pdf",
    "winhex-f.pdf",
    "Manuel WinHex.pdf",
]
FOLDERS = ["ProjectWorkingFolder", "ShellBagsExplorer"]
EXE = "CALC.EXE"

async def submit(page, candidate):
    result = await page.evaluate("""async ({gameId, challengeId, candidate}) => {
        const r = await fetch(`/api/game/${gameId}/challenges/${challengeId}`, {
            method:'POST', credentials:'include', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({flag:candidate})
        });
        return {status:r.status, text:await r.text()};
    }""", {"gameId":GAME_ID,"challengeId":CHALLENGE_ID,"candidate":candidate})
    if result["status"] != 200:
        return f"HTTP_{result['status']}"
    submit_id = json.loads(result["text"])
    for _ in range(30):
        await asyncio.sleep(0.35)
        status = await page.evaluate("""async ({gameId, challengeId, submitId}) => {
            const r = await fetch(`/api/game/${gameId}/challenges/${challengeId}/status/${submitId}`, {credentials:'include'});
            return {status:r.status,text:await r.text()};
        }""", {"gameId":GAME_ID,"challengeId":CHALLENGE_ID,"submitId":submit_id})
        if status["status"] != 200: return f"STATUS_HTTP_{status['status']}"
        value=json.loads(status["text"])
        if value != "FlagSubmitted": return value
    return "TIMEOUT"

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
        context=await browser.new_context(storage_state='state70.json')
        page=await context.new_page()
        await page.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
        checked=0
        for pdf in PDFS:
            for folder in FOLDERS:
                candidate=f"grodno{{{pdf}_{folder}_{EXE}}}"
                result=await submit(page,candidate)
                checked += 1
                print(json.dumps({"n":checked,"candidate":candidate,"result":result},ensure_ascii=False),flush=True)
                if result == 'Accepted':
                    await browser.close(); return
                await asyncio.sleep(0.35)
        await browser.close()

asyncio.run(main())
