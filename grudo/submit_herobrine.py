import asyncio
from playwright.async_api import async_playwright

CANDIDATE = "grodno{F1@G}"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(storage_state="state70.json")
        page = await context.new_page()
        await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)
        card = page.locator(".mantine-Card-root").filter(has_text="Herobrine")
        print("CARD_COUNT", await card.count())
        await card.first.evaluate("el => el.click()")
        await page.wait_for_selector(".mantine-Modal-content", timeout=10000)
        modal = page.locator(".mantine-Modal-content")
        inputs = modal.locator("input")
        target = None
        for i in range(await inputs.count()):
            el = inputs.nth(i)
            typ = (await el.get_attribute("type") or "").lower()
            placeholder = await el.get_attribute("placeholder") or ""
            if typ in ("text", "") and "flag" in placeholder.lower():
                target = el
                break
        if target is None:
            target = inputs.last
        await target.fill(CANDIDATE)
        submit = modal.locator("button:has-text('Submit Flag')")
        print("SUBMIT_COUNT", await submit.count())
        await submit.last.click()
        await page.wait_for_timeout(4000)
        body = await page.locator("body").inner_text()
        markers = [line.strip() for line in body.splitlines() if any(x in line.lower() for x in ["correct", "accepted", "incorrect", "wrong", "already solved", "success", "attempts left"])]
        print("CANDIDATE", CANDIDATE)
        print("RESULT_MARKERS", markers[-30:])
        if await modal.count():
            print("MODAL_TAIL", (await modal.inner_text())[-1500:])
        else:
            print("MODAL_CLOSED")
        await page.screenshot(path="herobrine_submit_result.png", full_page=True)
        await browser.close()

asyncio.run(main())
