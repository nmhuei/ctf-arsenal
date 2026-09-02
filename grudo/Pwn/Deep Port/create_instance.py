import asyncio
from playwright.async_api import async_playwright

BASE = "https://ctf-spcs.mf.grsu.by"
USER = "nmhuei"
PASSWORD = "Light@2025"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        async def log_response(resp):
            url = resp.url.lower()
            if any(k in url for k in ("instance", "challenge", "container", "game")):
                print(f"[RESP] {resp.status} {resp.url}")
                ctype = (resp.headers.get("content-type") or "").lower()
                if "json" in ctype:
                    try:
                        body = await resp.text()
                        print(f"[BODY] {body[:3000]}")
                    except Exception:
                        pass
        page.on("response", log_response)

        await page.goto(f"{BASE}/account/login?from=/games/2/challenges", wait_until="domcontentloaded")
        await page.wait_for_selector("input[type='password']", timeout=20000)
        await page.wait_for_timeout(2500)
        await page.fill("input[type='text']", USER)
        await page.fill("input[type='password']", PASSWORD)
        await page.wait_for_timeout(700)
        print("[DEBUG] login values:", await page.locator("input[type='text']").input_value(), len(await page.locator("input[type='password']").input_value()))
        await page.click("button:has-text('Login')")
        await page.wait_for_timeout(5000)
        print("[DEBUG] URL after login:", page.url)
        print("[DEBUG] BODY after login:\n", (await page.locator("body").inner_text())[:5000])
        await page.screenshot(path="login_after.png", full_page=True)
        await page.wait_for_selector(".mantine-Card-root:has-text('pts')", timeout=30000)
        print("[+] Login successful")

        cards = page.locator(".mantine-Card-root").filter(has_text="Deep Port")
        count = await cards.count()
        print(f"[+] Deep Port cards: {count}")
        if count == 0:
            print((await page.locator("body").inner_text())[:5000])
            return

        await cards.first.evaluate("el => el.click()")
        modal = page.locator(".mantine-Modal-content")
        await modal.wait_for(state="visible", timeout=10000)
        await page.wait_for_timeout(1000)
        print("--- MODAL BEFORE ---")
        print(await modal.inner_text())
        print("--- BUTTONS ---")
        buttons = modal.locator("button")
        for i in range(await buttons.count()):
            b = buttons.nth(i)
            print(i, repr((await b.inner_text()).strip()), await b.get_attribute("disabled"))

        create = modal.locator("button").filter(has_text="Create")
        if await create.count() == 0:
            print("[-] Create button not found")
            return
        print("[+] Clicking Create")
        await create.first.click()
        await page.wait_for_timeout(6000)
        print("--- MODAL AFTER ---")
        print(await modal.inner_text())
        print("--- PAGE TEXT TAIL ---")
        body = await page.locator("body").inner_text()
        print(body[-5000:])
        await context.storage_state(path="auth_instance.json")
        await browser.close()

asyncio.run(main())
