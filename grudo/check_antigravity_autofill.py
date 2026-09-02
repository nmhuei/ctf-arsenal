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
        await page.goto("https://ctf-spcs.mf.grsu.by/account/login?from=/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("input[type='password']", timeout=15000)
        await page.wait_for_timeout(2500)
        u=page.locator("input[type='text']")
        pw=page.locator("input[type='password']")
        print("USERNAME_FILLED", bool(await u.input_value()))
        print("PASSWORD_FILLED", bool(await pw.input_value()))
        await context.close()

asyncio.run(main())
