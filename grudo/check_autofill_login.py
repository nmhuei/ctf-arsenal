import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/home/light/.config/chromium",
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
            args=["--enable-features=PasswordImport"],
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://ctf-spcs.mf.grsu.by/account/login?from=/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("input[type='password']", timeout=15000)
        await page.wait_for_timeout(3000)
        u = page.locator("input[type='text']")
        pw = page.locator("input[type='password']")
        print("USERNAME_FILLED", bool(await u.input_value()))
        print("PASSWORD_FILLED", bool(await pw.input_value()))
        if await u.input_value() and await pw.input_value():
            await page.click("button:has-text('Login')")
            await page.wait_for_timeout(5000)
            print("URL_AFTER", page.url)
            text = await page.locator("body").inner_text()
            print("HAS_CHALLENGE", "Pinned to Yesterday" in text)
            print(text[:800])
        await context.close()

asyncio.run(main())
