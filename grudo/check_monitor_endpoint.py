import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(storage_state="state70.json")
        page = await context.new_page()
        await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        result = await page.evaluate("""async () => {
            const r = await fetch('/api/game/2/Submissions?count=1', {credentials:'include'});
            return {status:r.status, text:await r.text()};
        }""")
        print('STATUS', result['status'])
        print(result['text'][:500])
        await browser.close()

asyncio.run(main())
