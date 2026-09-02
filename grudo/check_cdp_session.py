import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        print("CONTEXTS", len(browser.contexts))
        for ci, context in enumerate(browser.contexts):
            print("CONTEXT", ci, "PAGES", len(context.pages))
            for pi, page in enumerate(context.pages):
                try:
                    print("PAGE", ci, pi, page.url, await page.title())
                except Exception as e:
                    print("PAGE_ERROR", ci, pi, type(e).__name__)
        await browser.close()

asyncio.run(main())
