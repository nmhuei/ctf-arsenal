import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/home/light/.gemini/antigravity-browser-profile",
            executable_path="/usr/lib/chromium/chromium",
            headless=True,
            args=["--no-first-run", "--no-default-browser-check"],
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        text = await page.locator("body").inner_text()
        print("URL", page.url)
        print("HAS_CHALLENGE", "Pinned to Yesterday" in text)
        print("LOGIN_REQUIRED", "Please Login" in text)
        print(text[:500])
        await context.close()

asyncio.run(main())
