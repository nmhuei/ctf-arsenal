import asyncio
import os
import json
import base64
import urllib.request
from playwright.async_api import async_playwright

async def main():
    # Workspace output directory
    workspace_dir = "/home/light/Workspace/CTF/grudo"
    os.makedirs(workspace_dir, exist_ok=True)
    
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(
            executable_path="/home/light/.cloakbrowser/chromium-146.0.7680.177.5/chrome",
            headless=True
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to login page
        print("Navigating to login page...")
        await page.goto("https://ctf-spcs.mf.grsu.by/account/login?from=/games/2/challenges")
        await page.wait_for_selector("input[type='password']")
        await page.wait_for_timeout(2000) # Wait for hydration
        
        # Fill credentials
        print("Filling credentials...")
        await page.fill("input[type='text']", "nmhuei")
        await page.fill("input[type='password']", "Light@2025")
        await page.wait_for_timeout(500)
        
        print("Clicking Login...")
        await page.click("button:has-text('Login')")
        
        # Wait for challenges page cards to load
        print("Waiting for challenges page to load...")
        try:
            await page.wait_for_selector(".mantine-Card-root:has-text('pts')", timeout=25000)
            print("Logged in successfully!")
        except Exception as e:
            print(f"Failed to find challenge cards: {e}")
            screenshot_path = os.path.join(workspace_dir, "login_error.png")
            await page.screenshot(path=screenshot_path)
            print(f"Saved error screenshot to {screenshot_path}")
            await browser.close()
            return
            
        # Get count of total challenge cards in default 'All' view
        cards_locator = page.locator(".mantine-Card-root").filter(has_text="pts")
        cards_count = await cards_locator.count()
        print(f"Found {cards_count} challenge cards on 'All' view.")
        
        # 1. Scrape details for all challenges
        all_challenges_data = []
        
        print("\n--- Scraping All Challenges ---")
        for i in range(cards_count):
            # Query locator dynamically to avoid stale elements
            card = page.locator(".mantine-Card-root").filter(has_text="pts").nth(i)
            card_text = await card.inner_text()
            title = card_text.split('\n')[0].strip()
            
            print(f"[{i+1}/{cards_count}] Scraping: {title}")
            
            # Click to open modal using native DOM click (bypasses pointer-event / overlay interception)
            await card.evaluate("el => el.click()")
            
            modal_selector = ".mantine-Modal-content"
            await page.wait_for_selector(modal_selector, timeout=10000)
            
            # Wait for modal text to update to current challenge title
            try:
                await page.wait_for_function(
                    "([selector, title]) => { const el = document.querySelector(selector); return el && el.innerText && el.innerText.includes(title); }",
                    arg=[modal_selector, title],
                    timeout=8000
                )
            except Exception as e:
                print(f"  [Timeout] Modal did not update to show '{title}', attempting re-click...")
                close_btn = page.locator(".mantine-Modal-close")
                if await close_btn.count() > 0:
                    await close_btn.first.evaluate("el => el.click()")
                    await page.wait_for_timeout(500)
                await card.evaluate("el => el.click()")
                await page.wait_for_function(
                    "([selector, title]) => { const el = document.querySelector(selector); return el && el.innerText && el.innerText.includes(title); }",
                    arg=[modal_selector, title],
                    timeout=8000
                )
                
            modal = page.locator(modal_selector)
            modal_text = await modal.inner_text()
            
            # Extract links inside modal
            attachment_links = []
            links = await modal.locator("a").all()
            for l in links:
                href = await l.get_attribute("href")
                link_text = await l.inner_text()
                if href and ("/assets/" in href or "attachment" in link_text.lower() or "download" in link_text.lower()):
                    full_url = href if href.startswith("http") else f"https://ctf-spcs.mf.grsu.by{href}"
                    attachment_links.append({
                        "text": link_text.strip(),
                        "url": full_url
                    })
                    
            # Parse basic challenge metadata from modal text
            lines = [line.strip() for line in modal_text.split('\n') if line.strip()]
            points = None
            author = None
            solves = None
            
            for line in lines:
                if "pts" in line:
                    points = line
                if "Author:" in line:
                    author = line
                if "SOLVES" in line or "solves" in line.lower():
                    solves = line
                    
            challenge_info = {
                "title": title,
                "points": points,
                "solves": solves,
                "author": author,
                "attachments": attachment_links,
                "raw_text": modal_text
            }
            all_challenges_data.append(challenge_info)
            
            # Close the modal using native click
            close_btn = page.locator(".mantine-Modal-close")
            if await close_btn.count() > 0:
                await close_btn.first.evaluate("el => el.click()")
            else:
                await page.keyboard.press("Escape")
                
            # Wait for modal content to be hidden
            await page.wait_for_selector(modal_selector, state="hidden", timeout=5000)
            await page.wait_for_timeout(1200)
            
        # 2. Build Title to Category Mapping
        categories = ["Misc", "Crypto", "Pwn", "Web", "Reverse", "Forensics", "AI", "OSINT"]
        title_to_category = {}
        
        print("\n--- Mapping Challenges to Categories ---")
        for cat in categories:
            tab_locator = page.locator("button[role='tab']").filter(has_text=cat)
            if await tab_locator.count() == 0:
                tab_locator = page.locator(".mantine-Tabs-tab").filter(has_text=cat)
                
            if await tab_locator.count() > 0:
                print(f"Filtering category: {cat}...")
                await tab_locator.first.click()
                await page.wait_for_timeout(1000)
                
                # List visible cards
                cards = page.locator(".mantine-Card-root").filter(has_text="pts")
                count = await cards.count()
                for i in range(count):
                    card_text = await cards.nth(i).inner_text()
                    title = card_text.split('\n')[0].strip()
                    title_to_category[title] = cat
                    print(f"  - [{cat}] {title}")
            else:
                print(f"WARNING: Tab button for category '{cat}' not found!")
                
        # 3. Create folders, download attachments, and write READMEs
        print("\n--- Downloading Attachments & Writing Files ---")
        for idx, chal in enumerate(all_challenges_data):
            title = chal["title"]
            category = title_to_category.get(title, "Misc")
            
            print(f"[{idx+1}/{len(all_challenges_data)}] Processing: {title} (Category: {category})")
            
            # Create challenge directory
            clean_title = "".join(c for c in title if c.isalnum() or c in " -_.").strip()
            challenge_dir = os.path.join(workspace_dir, category, clean_title)
            os.makedirs(challenge_dir, exist_ok=True)
            
            # Download attachments
            for att_idx, att in enumerate(chal["attachments"]):
                att_url = att["url"]
                att_name = att["text"]
                if not att_name:
                    att_name = f"attachment_{att_idx+1}"
                    
                clean_att_name = "".join(c for c in att_name if c.isalnum() or c in " -_.").strip()
                url_filename = att_url.split('/')[-1].split('?')[0]
                if '.' not in clean_att_name and '.' in url_filename:
                    clean_att_name += url_filename[url_filename.rfind('.'):]
                    
                print(f"  Downloading attachment: '{clean_att_name}'")
                
                # Fetch inside page context to preserve cookies/auth
                try:
                    base64_data = await page.evaluate("""async (url) => {
                        const response = await fetch(url);
                        if (!response.ok) throw new Error('HTTP status ' + response.status);
                        const blob = await response.blob();
                        return new Promise((resolve, reject) => {
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                const base64data = reader.result.split(',')[1];
                                resolve(base64data);
                            };
                            reader.onerror = reject;
                            reader.readAsDataURL(blob);
                        });
                    }""", att_url)
                    
                    file_path = os.path.join(challenge_dir, clean_att_name)
                    with open(file_path, "wb") as f:
                        f.write(base64.b64decode(base64_data))
                    print("    Saved successfully.")
                except Exception as eval_err:
                    print(f"    Failed via page context: {eval_err}. Trying urllib...")
                    try:
                        file_path = os.path.join(challenge_dir, clean_att_name)
                        urllib.request.urlretrieve(att_url, file_path)
                        print("    Saved successfully via urllib.")
                    except Exception as urllib_err:
                        print(f"    ERROR downloading '{clean_att_name}': {urllib_err}")
                        
            # Write README.md
            readme_path = os.path.join(challenge_dir, "README.md")
            readme_content = f"# {title}\n\n"
            if chal["points"]:
                readme_content += f"**Point Value**: {chal['points']}\n"
            if chal["solves"]:
                readme_content += f"**Solves**: {chal['solves']}\n"
            if chal["author"]:
                readme_content += f"**{chal['author']}**\n"
            readme_content += "\n## Description\n\n"
            
            # Extract description
            desc_lines = []
            for line in chal["raw_text"].split('\n'):
                line_strip = line.strip()
                if not line_strip:
                    continue
                if line_strip == title:
                    continue
                if chal["points"] and line_strip == chal["points"]:
                    continue
                if chal["author"] and line_strip == chal["author"]:
                    continue
                if line_strip == "Submit Flag":
                    break
                desc_lines.append(line)
                
            readme_content += "\n".join(desc_lines).strip() + "\n\n"
            
            if chal["attachments"]:
                readme_content += "## Attachments\n\n"
                for att in chal["attachments"]:
                    readme_content += f"- [{att['text']}]({att['url']})\n"
                    
            with open(readme_path, "w") as f:
                f.write(readme_content)
            print("  Saved README.md.")
            
        # Save a master JSON backup of all correct challenge data
        master_json_path = os.path.join(workspace_dir, "challenges_metadata_correct.json")
        with open(master_json_path, "w") as f:
            json.dump(all_challenges_data, f, indent=2)
        print(f"\nSaved master JSON data to {master_json_path}")
        print("All downloads and structure completed successfully!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
