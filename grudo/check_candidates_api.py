import asyncio
import json
import sys
from playwright.async_api import async_playwright

GAME_ID = 2
CHALLENGE_ID = 77

async def submit(page, candidate: str) -> str:
    result = await page.evaluate(
        """async ({gameId, challengeId, candidate}) => {
            const r = await fetch(`/api/game/${gameId}/challenges/${challengeId}`, {
                method: 'POST',
                credentials: 'include',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({flag: candidate})
            });
            return {status: r.status, text: await r.text()};
        }""",
        {"gameId": GAME_ID, "challengeId": CHALLENGE_ID, "candidate": candidate},
    )
    if result["status"] != 200:
        return f"HTTP_{result['status']}:{result['text'][:200]}"
    submit_id = json.loads(result["text"])
    for _ in range(30):
        await asyncio.sleep(0.5)
        status = await page.evaluate(
            """async ({gameId, challengeId, submitId}) => {
                const r = await fetch(`/api/game/${gameId}/challenges/${challengeId}/status/${submitId}`, {credentials:'include'});
                return {status:r.status, text:await r.text()};
            }""",
            {"gameId": GAME_ID, "challengeId": CHALLENGE_ID, "submitId": submit_id},
        )
        if status["status"] != 200:
            return f"STATUS_HTTP_{status['status']}:{status['text'][:200]}"
        value = json.loads(status["text"])
        if value != "FlagSubmitted":
            return str(value)
    return "TIMEOUT"

async def main(candidates):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(storage_state="state70.json")
        page = await context.new_page()
        await page.goto("https://ctf-spcs.mf.grsu.by/games/2/challenges", wait_until="domcontentloaded", timeout=30000)
        for candidate in candidates:
            answer = await submit(page, candidate)
            print(json.dumps({"candidate": candidate, "result": answer}, ensure_ascii=False), flush=True)
            if answer == "Accepted":
                break
            await asyncio.sleep(0.7)
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: check_candidates_api.py FLAG [FLAG ...]")
    asyncio.run(main(sys.argv[1:]))
