import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome',headless=True)
        context=await browser.new_context(storage_state='state70.json')
        page=await context.new_page()
        await page.goto('https://ctf-spcs.mf.grsu.by/games/2/challenges',wait_until='domcontentloaded',timeout=30000)
        await page.wait_for_timeout(5000)
        print('URL',page.url)
        print('CARDCOUNT',await page.locator('.mantine-Card-root').count())
        exact=page.get_by_text('Pinned to Yesterday',exact=True)
        print('EXACTCOUNT',await exact.count())
        for i in range(await exact.count()):
            el=exact.nth(i)
            print('EL',i,await el.evaluate("e=>e.outerHTML"))
            print('PARENT',await el.evaluate("e=>e.parentElement?.outerHTML.slice(0,2000)"))
        body=await page.locator('body').inner_text()
        print('INDEX',body.find('Pinned to Yesterday'))
        print(body[max(0,body.find('Pinned to Yesterday')-200):body.find('Pinned to Yesterday')+500])
        await browser.close()
asyncio.run(main())
