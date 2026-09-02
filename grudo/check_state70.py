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
        await page.wait_for_timeout(3000)
        text = await page.locator("body").inner_text()
        print("URL", page.url)
        print("AUTHENTICATED", "Pinned to Yesterday" in text)
        print("LOGIN_PAGE", "/account/login" in page.url)
        await browser.close()

asyncio.run(main())
