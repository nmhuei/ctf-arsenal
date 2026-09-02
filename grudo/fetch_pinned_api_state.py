import asyncio, json
from playwright.async_api import async_playwright

URLS = [
    "https://ctf-spcs.mf.grsu.by/api/game/2/challenges/77",
    "https://ctf-spcs.mf.grsu.by/api/game/2/challenges",
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(storage_state="state70.json")
        page = await context.new_page()
        await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        for url in URLS:
            result = await page.evaluate("""async (url) => {
                const r = await fetch(url, {credentials:'include'});
                return {status:r.status, text:await r.text()};
            }""", url)
            print("URL", url, "STATUS", result["status"])
            try:
                obj=json.loads(result["text"])
                print(json.dumps(obj,ensure_ascii=False,indent=2))
            except Exception:
                print(result["text"][:10000])
        await browser.close()

asyncio.run(main())
