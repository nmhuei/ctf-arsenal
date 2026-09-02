# cookoff local solver

## Bug

`admin.js` leaks `process.env.FLAG` directly to stdout in `/bot/run`:

```js
console.log(process.env.FLAG)
```

The bot also logs `document.cookie` after setting the flag cookie. In local mode, the solver starts a dependency-free harness that preserves these leaks and proves the extracted flag is the real cookie-backed flag by checking for `flag<FLAG>` in the bot log.

## Run local

From the extracted challenge directory:

```bash
python3 solution/solve_cookoff.py --local
```

Custom fake local flag:

```bash
python3 solution/solve_cookoff.py --local --flag 'GPNCTF{test_flag_123}'
```

## Run against a remote HTTP deployment

```bash
python3 solution/solve_cookoff.py --remote https://HOST
```

This will hit `/bot/run?url=http://localhost:1337/`. If the deployment returns process stdout/stderr to the client, the solver extracts `GPNCTF{...}` from the response. If stdout is hidden, this specific debug-log leak is not directly visible over HTTP and a browser-side XSS chain would be required.
