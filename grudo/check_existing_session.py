import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/home/light/.config/chromium",
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)
        print("URL", page.url)
        text = await page.locator("body").inner_text()
        print("HAS_CHALLENGE", "Pinned to Yesterday" in text)
        print(text[:1200])
        await context.close()

asyncio.run(main())
