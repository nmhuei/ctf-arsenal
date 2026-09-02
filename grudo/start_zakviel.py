import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://ctf-spcs.mf.grsu.by"
CHALLENGE = "Zakviel"


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
            headless=True,
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
        count = await cards.count()
        if count < 1:
            raise RuntimeError("Zakviel card not found")
        await cards.first.evaluate("el => el.click()")
        modal = page.locator(".mantine-Modal-content")
        await modal.wait_for(state="visible", timeout=15000)
        await page.wait_for_timeout(1500)
        print("=== MODAL BEFORE ===")
        print(await modal.inner_text())
        print("=== BUTTONS ===")
        for i in range(await modal.locator("button").count()):
            b = modal.locator("button").nth(i)
            print(i, repr((await b.inner_text()).strip()), await b.is_enabled())

        create = modal.locator("button").filter(has_text=re.compile(r"^Create$", re.I))
        if await create.count() > 0 and await create.first.is_enabled():
            before = len(responses)
            await create.first.click()
            await page.wait_for_timeout(5000)
            print("=== MODAL AFTER CREATE ===")
            print(await modal.inner_text())
            print("=== RELEVANT RESPONSES ===")
            for st, method, url in responses[before:]:
                if any(x in url.lower() for x in ["instance", "challenge", "game"]):
                    print(st, method, url)
        else:
            print("=== NO CREATE ACTION (possibly active instance) ===")

        # Extract IPv4:port and URLs from visible modal text/HTML.
        text = await modal.inner_text()
        html = await modal.inner_html()
        found = sorted(set(re.findall(r"(?:https?://)?(?:\d{1,3}\.){3}\d{1,3}:\d+", text + "\n" + html)))
        print("=== ENDPOINTS ===")
        for x in found:
            print(x)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
