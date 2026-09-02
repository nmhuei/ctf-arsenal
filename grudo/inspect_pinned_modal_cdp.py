import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        try:
            await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector(".mantine-Card-root", timeout=15000)
            cards = page.locator(".mantine-Card-root").filter(has_text="Pinned to Yesterday")
            print("CARD_COUNT", await cards.count())
            await cards.first.evaluate("el => el.click()")
            await page.wait_for_selector(".mantine-Modal-content", timeout=10000)
            modal = page.locator(".mantine-Modal-content")
            print("MODAL_TEXT\n", await modal.inner_text())
            print("INPUTS", await modal.locator("input").count())
            for i in range(await modal.locator("input").count()):
                el=modal.locator("input").nth(i)
                print("INPUT",i,"type",await el.get_attribute("type"),"placeholder",await el.get_attribute("placeholder"))
            print("BUTTONS",await modal.locator("button").count())
            for i in range(await modal.locator("button").count()):
                el=modal.locator("button").nth(i)
                print("BUTTON",i,repr((await el.inner_text()).strip()))
        finally:
            await page.close()
            await browser.close()

asyncio.run(main())
