import asyncio
from playwright.async_api import async_playwright

BASE = "https://ctf-spcs.mf.grsu.by"
USER = "nmhuei"
PASSWORD = "Light@2025"
FLAG = "grodno{b8147a5d-1aeb-4fc5-8c39-8986e772e054}"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        async def log_response(resp):
            u = resp.url.lower()
            if any(k in u for k in ("submit", "challenge", "game/2")):
                print(f"[RESP] {resp.status} {resp.url}")
                ctype = (resp.headers.get("content-type") or "").lower()
                if "json" in ctype:
                    try:
                        print("[BODY]", (await resp.text())[:3000])
                    except Exception:
                        pass
        page.on("response", log_response)

        await page.goto(f"{BASE}/account/login?from=/games/2/challenges", wait_until="domcontentloaded")
        await page.wait_for_selector("input[type='password']", timeout=20000)
        await page.wait_for_timeout(2500)
        await page.fill("input[type='text']", USER)
        await page.fill("input[type='password']", PASSWORD)
        await page.wait_for_timeout(700)
        await page.click("button:has-text('Login')")
        await page.wait_for_selector(".mantine-Card-root:has-text('pts')", timeout=30000)

        card = page.locator(".mantine-Card-root").filter(has_text="Deep Port").first
        await card.evaluate("el => el.click()")
        modal = page.locator(".mantine-Modal-content")
        await modal.wait_for(state="visible", timeout=10000)
        await page.wait_for_timeout(700)

        submit_button = modal.locator("button").filter(has_text="Submit Flag").first
        await submit_button.click()
        await page.wait_for_timeout(800)
        print("--- AFTER OPEN SUBMIT ---")
        print(await modal.inner_text())

        inputs = modal.locator("input:visible")
        count = await inputs.count()
        print("visible inputs:", count)
        if count == 0:
            raise RuntimeError("no visible flag input")
        flag_input = inputs.nth(count - 1)
        print("placeholder:", await flag_input.get_attribute("placeholder"))
        await flag_input.fill(FLAG)

        buttons = modal.locator("button:visible")
        for i in range(await buttons.count()):
            print("button", i, repr((await buttons.nth(i).inner_text()).strip()))

        candidates = modal.locator("button:visible").filter(has_text="Submit")
        clicked = False
        for i in range(await candidates.count()):
            text = (await candidates.nth(i).inner_text()).strip()
            if text == "Submit" or text == "Submit Flag":
                await candidates.nth(i).click()
                clicked = True
                break
        if not clicked:
            raise RuntimeError("submit confirmation button not found")

        await page.wait_for_timeout(2500)
        print("--- RESULT BODY ---")
        print((await page.locator("body").inner_text())[-4000:])
        await browser.close()

asyncio.run(main())
