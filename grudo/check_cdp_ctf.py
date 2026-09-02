import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        try:
            await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(4000)
            text = await page.locator("body").inner_text()
            print("URL", page.url)
            print("HAS_CHALLENGE", "Pinned to Yesterday" in text)
            print("LOGIN_REQUIRED", "Please Login" in text or "Login" in text[:500])
            print(text[:1200])
        finally:
            await page.close()
            await browser.close()

asyncio.run(main())
