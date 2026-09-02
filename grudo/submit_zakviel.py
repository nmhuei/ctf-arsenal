import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

FLAG = "grodno{dd8bccb3-ea68-435e-9348-6970385ee0dd}"
BASE = "https://ctf-spcs.mf.grsu.by"


def credentials():
    src = Path("CTF/grudo/download_challenges.py").read_text(encoding="utf-8")
    u = re.search(r'page\.fill\("input\[type=\'text\'\]",\s*"([^"]+)"\)', src)
    p = re.search(r'page\.fill\("input\[type=\'password\'\]",\s*"([^"]+)"\)', src)
    if not u or not p:
        raise RuntimeError("saved credentials not found")
    return u.group(1), p.group(1)


async def main():
    username, password = credentials()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        page = await browser.new_page()
        captured = []

        async def record_response(resp):
            if resp.request.method == "POST" and "/api/game/" in resp.url:
                try:
                    body = await resp.text()
                except Exception:
                    body = "<unreadable>"
                captured.append((resp.status, resp.request.method, resp.url, body[:2000]))

        page.on("response", record_response)
        await page.goto(f"{BASE}/account/login?from=/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("input[type='password']", timeout=20000)
        await page.fill("input[type='text']", username)
        await page.fill("input[type='password']", password)
        await page.click("button:has-text('Login')")
        await page.wait_for_selector(".mantine-Card-root:has-text('pts')", timeout=30000)

        card = page.locator(".mantine-Card-root").filter(has_text="Zakviel")
        if await card.count() < 1:
            raise RuntimeError("Zakviel card not found")
        await card.first.evaluate("el => el.click()")
        modal = page.locator(".mantine-Modal-content")
        await modal.wait_for(state="visible", timeout=15000)

        inputs = modal.locator("input")
        target = None
        for i in range(await inputs.count()):
            el = inputs.nth(i)
            typ = (await el.get_attribute("type") or "").lower()
            ph = await el.get_attribute("placeholder") or ""
            if typ in ("text", "") and "flag" in ph.lower():
                target = el
                break
        if target is None and await inputs.count() > 0:
            target = inputs.last
        if target is None:
            raise RuntimeError("flag input not found")

        await target.fill(FLAG)
        submit = modal.locator("button:has-text('Submit Flag')")
        if await submit.count() < 1:
            submit = modal.locator("button:has-text('Submit')")
        if await submit.count() < 1:
            raise RuntimeError("submit button not found")

        await submit.last.click()
        await page.wait_for_timeout(4000)
        body = await page.locator("body").inner_text()
        markers = [line.strip() for line in body.splitlines() if any(w in line.lower() for w in ("correct", "accepted", "incorrect", "wrong", "solved", "success"))]
        print("FLAG", FLAG)
        print("RESULT_MARKERS", markers[-30:])
        print("MODAL_TEXT", (await modal.inner_text())[-1600:] if await modal.count() else "<closed>")
        print("POST_RESPONSES")
        for item in captured:
            print(item)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
