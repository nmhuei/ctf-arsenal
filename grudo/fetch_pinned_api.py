import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        try:
            await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
            for url in [
                "https://ctf-spcs.mf.grsu.by/api/game/2/challenges/77",
                "https://ctf-spcs.mf.grsu.by/api/game/2/challenges/77/status/30460",
            ]:
                result = await page.evaluate("""async (url) => {
                    const r = await fetch(url, {credentials:'include'});
                    return {status:r.status, text:await r.text()};
                }""", url)
                print("URL", url, "STATUS", result["status"])
                try:
                    obj=json.loads(result["text"])
                    print(json.dumps(obj,ensure_ascii=False,indent=2))
                except Exception:
                    print(result["text"][:5000])
        finally:
            await page.close(); await browser.close()

asyncio.run(main())
