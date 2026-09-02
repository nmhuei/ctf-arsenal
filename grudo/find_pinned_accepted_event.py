import asyncio
import json
from playwright.async_api import async_playwright

GAME_ID = 2
CHALLENGE_ID = "77"
PAGE_SIZE = 100
MAX_PAGES = 200

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True,
        )
        context = await browser.new_context(storage_state="state70.json")
        page = await context.new_page()
        await page.goto(f"https://ctf-spcs.mf.grsu.by/games/{GAME_ID}/challenges", wait_until="domcontentloaded", timeout=30000)

        found = []
        total_seen = 0
        for page_num in range(MAX_PAGES):
            skip = page_num * PAGE_SIZE
            result = await page.evaluate(
                """async ({gameId, count, skip}) => {
                    const r = await fetch(`/api/game/${gameId}/events?hideContainer=true&count=${count}&skip=${skip}`, {credentials:'include'});
                    return {status:r.status, text:await r.text()};
                }""",
                {"gameId": GAME_ID, "count": PAGE_SIZE, "skip": skip},
            )
            if result["status"] != 200:
                raise RuntimeError(f"HTTP {result['status']}: {result['text'][:300]}")
            events = json.loads(result["text"])
            total_seen += len(events)
            for event in events:
                values = event.get("values") or event.get("Values") or []
                if len(values) < 4:
                    continue
                answer_result, submitted_answer, challenge_name, challenge_id = values[:4]
                if str(challenge_id) == CHALLENGE_ID and str(answer_result).lower() == "accepted":
                    found.append({
                        "time": event.get("time") or event.get("publishTimeUtc"),
                        "team": event.get("team"),
                        "user": event.get("user"),
                        "challenge": challenge_name,
                        "challenge_id": challenge_id,
                        "result": answer_result,
                        "answer": submitted_answer,
                    })
            if found or len(events) < PAGE_SIZE:
                break

        print(json.dumps({"events_scanned": total_seen, "accepted_events": found}, ensure_ascii=False, indent=2))
        await browser.close()

asyncio.run(main())
