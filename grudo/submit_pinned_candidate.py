import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

CANDIDATE = "grodno{OJYBIB.pdf_ShellBagsExplorer_CALC.EXE}"

async def main():
    source = Path("download_challenges.py").read_text(encoding="utf-8")
    username = re.search(r'page\.fill\("input\[type=\'text\'\]", "([^"]+)"\)', source).group(1)
    password = re.search(r'page\.fill\("input\[type=\'password\'\]", "([^"]+)"\)', source).group(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        page = await browser.new_page()
        await page.goto(
            "https://ctf-spcs.mf.grsu.by/account/login?from=/games/2/challenges",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await page.wait_for_selector("input[type='password']", timeout=15000)
        await page.fill("input[type='text']", username)
        await page.fill("input[type='password']", password)
        await page.click("button:has-text('Login')")
        await page.wait_for_timeout(5000)

        print("URL_AFTER_LOGIN", page.url)
        body_text = await page.locator("body").inner_text()
        if "Pinned to Yesterday" not in body_text:
            print("LOGIN_OR_PAGE_FAILURE")
            print(body_text[:1200])
            await browser.close()
            return

        card = page.locator(".mantine-Card-root").filter(has_text="Pinned to Yesterday")
        print("CARD_COUNT", await card.count())
        await card.first.evaluate("el => el.click()")
        await page.wait_for_selector(".mantine-Modal-content", timeout=10000)
        modal = page.locator(".mantine-Modal-content")

        inputs = modal.locator("input")
        print("INPUT_COUNT", await inputs.count())
        target = None
        for i in range(await inputs.count()):
            el = inputs.nth(i)
            typ = (await el.get_attribute("type") or "").lower()
            placeholder = await el.get_attribute("placeholder") or ""
            if typ in ("text", "") and "flag" in placeholder.lower():
                target = el
                break
        if target is None and await inputs.count() > 0:
            target = inputs.last
        if target is None:
            print("NO_FLAG_INPUT")
            print((await modal.inner_text())[-1000:])
            await browser.close()
            return

        await target.fill(CANDIDATE)
        buttons = modal.locator("button")
        submit = modal.locator("button:has-text('Submit Flag')")
        if await submit.count() == 0:
            submit = modal.locator("button:has-text('Submit')")
        print("SUBMIT_COUNT", await submit.count())
        if await submit.count() == 0:
            print("NO_SUBMIT_BUTTON")
            print((await modal.inner_text())[-1000:])
            await browser.close()
            return

        await submit.last.click()
        await page.wait_for_timeout(3500)
        result_text = await page.locator("body").inner_text()
        print("CANDIDATE", CANDIDATE)
        markers = [line.strip() for line in result_text.splitlines() if any(x in line.lower() for x in ["correct", "accepted", "incorrect", "wrong", "already solved", "success"])]
        print("RESULT_MARKERS", markers[-20:])
        print("MODAL_TAIL", (await modal.inner_text())[-1200:] if await modal.count() else "MODAL_CLOSED")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
