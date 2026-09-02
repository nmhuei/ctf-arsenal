import asyncio
import sys
from playwright.async_api import async_playwright

async def main(candidate: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(storage_state="state70.json")
        page = await context.new_page()
        try:
            await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
            title = page.get_by_text("Pinned to Yesterday", exact=True)
            await title.wait_for(timeout=15000)
            await title.evaluate("el => el.closest('.mantine-Card-root').click()")
            await page.wait_for_selector(".mantine-Modal-content", timeout=10000)
            modal = page.locator(".mantine-Modal-content")
            before = await modal.inner_text()
            print("BEFORE", [line.strip() for line in before.splitlines() if "tried" in line.lower() or "solved" in line.lower()])
            inp = modal.locator("input").first
            await inp.fill(candidate)
            await modal.locator("button:has-text('Submit Flag')").click()
            await page.wait_for_timeout(3500)
            text = await page.locator("body").inner_text()
            markers = [
                line.strip() for line in text.splitlines()
                if any(k in line.lower() for k in ["correct", "accepted", "wrong", "solved", "success", "attempt"])
            ]
            print("CANDIDATE", candidate)
            print("RESULT", markers[-30:])
            print("MODAL", (await modal.inner_text())[-700:] if await modal.count() else "closed")
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: submit_pinned_state.py FLAG")
    asyncio.run(main(sys.argv[1]))
