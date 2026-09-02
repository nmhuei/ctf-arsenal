import asyncio
import sys
from playwright.async_api import async_playwright

async def main(candidate: str):
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = await context.new_page()
        responses = []
        page.on("response", lambda r: responses.append((r.status, r.url)) if any(x in r.url.lower() for x in ["flag", "submit", "challenge", "attempt"]) else None)
        try:
            await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector(".mantine-Card-root", timeout=15000)
            cards = page.locator(".mantine-Card-root").filter(has_text="Pinned to Yesterday")
            await cards.first.evaluate("el => el.click()")
            await page.wait_for_selector(".mantine-Modal-content", timeout=10000)
            modal = page.locator(".mantine-Modal-content")
            before = await modal.inner_text()
            print("BEFORE_ATTEMPTS", [x for x in before.splitlines() if "tried" in x.lower()])
            inp = modal.locator("input").first
            await inp.fill(candidate)
            await modal.locator("button:has-text('Submit Flag')").click()
            await page.wait_for_timeout(3500)
            body = await page.locator("body").inner_text()
            modal_text = await modal.inner_text() if await modal.count() else ""
            interesting = []
            for line in body.splitlines():
                low=line.lower().strip()
                if any(k in low for k in ["correct", "accepted", "incorrect", "wrong", "success", "solved", "try", "flag"]):
                    interesting.append(line.strip())
            print("CANDIDATE", candidate)
            print("INTERESTING", interesting[-40:])
            print("MODAL_TAIL", modal_text[-800:])
            print("RESPONSES", responses[-20:])
        finally:
            await page.close()
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: submit_pinned_cdp.py FLAG")
    asyncio.run(main(sys.argv[1]))
