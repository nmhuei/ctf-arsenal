import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(storage_state="state70.json")
        page = await context.new_page()

        async def on_response(resp):
            url = resp.url
            if any(k in url.lower() for k in ["api/", "challenge", "game"]):
                try:
                    ct = resp.headers.get("content-type", "")
                    text = await resp.text()
                    print("RESPONSE", resp.status, url, "CT", ct)
                    print(text[:8000].replace("\x00", ""))
                except Exception as e:
                    print("RESPONSE_ERR", url, repr(e))
        page.on("response", on_response)

        await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(7000)
        print("PAGE_URL", page.url)
        body = await page.locator("body").inner_text()
        print("HAS_HEROBRINE", "Herobrine" in body, "BODY_LEN", len(body))
        cards = page.locator(".mantine-Card-root").filter(has_text="Herobrine")
        print("CARD_COUNT", await cards.count())
        if await cards.count():
            await cards.first.evaluate("el => el.click()")
            await page.wait_for_timeout(5000)
            modal = page.locator(".mantine-Modal-content")
            print("MODAL_COUNT", await modal.count())
            if await modal.count():
                print("MODAL_TEXT\n", (await modal.inner_text())[:10000])
        await page.wait_for_timeout(2000)
        await browser.close()

asyncio.run(main())
