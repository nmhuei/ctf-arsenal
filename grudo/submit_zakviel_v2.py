import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://ctf-spcs.mf.grsu.by"
CHALLENGE = "Zakviel"
FLAG = "grodno{dd8bccb3-ea68-435e-9348-6970385ee0dd}"


def extract_credentials():
    src = Path("CTF/grudo/download_challenges.py").read_text(encoding="utf-8")
    user_m = re.search(r'page\.fill\("input\[type=\'text\'\]",\s*"([^"]+)"\)', src)
    pass_m = re.search(r'page\.fill\("input\[type=\'password\'\]",\s*"([^"]+)"\)', src)
    if not user_m or not pass_m:
        raise RuntimeError("Could not locate saved login credentials")
    return user_m.group(1), pass_m.group(1)


async def main():
    username, password = extract_credentials()
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True
        )
        context = await browser.new_context()
        page = await context.new_page()
        responses = []
        page.on("response", lambda r: responses.append((r.status, r.request.method, r.url)))

        await page.goto(f"{BASE}/account/login?from=/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("input[type='password']", timeout=20000)
        await page.fill("input[type='text']", username)
        await page.fill("input[type='password']", password)
        await page.click("button:has-text('Login')")
        await page.wait_for_selector(".mantine-Card-root:has-text('pts')", timeout=30000)

        cards = page.locator(".mantine-Card-root").filter(has_text=CHALLENGE)
        if await cards.count() < 1:
            raise RuntimeError("Zakviel card not found")
        await cards.first.evaluate("el => el.click()")
        modal = page.locator(".mantine-Modal-content")
        await modal.wait_for(state="visible", timeout=15000)
        await page.wait_for_timeout(1000)

        print("=== MODAL BEFORE SUBMIT ===")
        print(await modal.inner_text())
        print("=== INPUTS ===")
        inputs = modal.locator("input")
        target = None
        for i in range(await inputs.count()):
            el = inputs.nth(i)
            print(i, await el.get_attribute("type"), await el.get_attribute("placeholder"), await el.is_visible())
            ph = (await el.get_attribute("placeholder") or "").lower()
            typ = (await el.get_attribute("type") or "").lower()
            if target is None and typ in ("", "text") and "flag" in ph and not await el.is_disabled():
                target = el
        if target is None:
            raise RuntimeError("flag input not found")

        await target.fill(FLAG)
        submit = modal.locator("button:has-text('Submit Flag')")
        if await submit.count() < 1:
            raise RuntimeError("Submit Flag button not found")

        before = len(responses)
        async with page.expect_response(lambda r: r.request.method == "POST" and "/api/game/" in r.url, timeout=20000) as response_info:
            await submit.last.click()
        response = await response_info.value
        try:
            response_body = await response.text()
        except Exception as exc:
            response_body = f"<cannot read: {exc}>"

        await page.wait_for_timeout(2500)
        body_text = await page.locator("body").inner_text()
        markers = [line.strip() for line in body_text.splitlines() if any(x in line.lower() for x in ["correct", "accepted", "incorrect", "wrong", "already solved", "success", "solved"])]
        print("=== SUBMISSION ===")
        print("FLAG", FLAG)
        print("HTTP", response.status, response.request.method, response.url)
        print("RESPONSE_BODY", response_body)
        print("RESULT_MARKERS", markers[-30:])
        print("MODAL_AFTER", (await modal.inner_text())[-1600:] if await modal.count() else "<closed>")
        print("RELEVANT_RESPONSES")
        for st, method, url in responses[before:]:
            if "/api/game/" in url:
                print(st, method, url)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
