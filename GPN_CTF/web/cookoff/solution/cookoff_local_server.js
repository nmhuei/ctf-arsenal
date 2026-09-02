#!/usr/bin/env node
'use strict';

/*
 * Dependency-free local harness for the cookoff challenge.
 * It serves the handout index.html on :1337 and a bot-compatible endpoint on :8080.
 * The important challenge bug is preserved: /bot/run logs process.env.FLAG and
 * later logs the cookie string containing that flag.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const ROOT = process.env.COOKOFF_ROOT || path.resolve(__dirname, '..', 'cookoff');
const FLAG = process.env.FLAG || 'GPNCTF{LOCAL_FAKE_FLAG_DEBUG_LOG_LEAK_PROOF}';
const HOST = '127.0.0.1';
const WEB_PORT = Number(process.env.WEB_PORT || 1337);
const BOT_PORT = Number(process.env.BOT_PORT || 8080);

function send(res, status, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(status, { 'content-type': type, 'cache-control': 'no-store' });
  res.end(body);
}

const web = http.createServer((req, res) => {
  const u = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (u.pathname === '/' || u.pathname === '/index.html') {
    const indexPath = path.join(ROOT, 'index.html');
    return fs.readFile(indexPath, (err, data) => {
      if (err) return send(res, 500, `cannot read ${indexPath}: ${err.message}`);
      send(res, 200, data, 'text/html; charset=utf-8');
    });
  }
  send(res, 404, 'not found');
});

function httpGet(url) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => {
      res.resume();
      res.on('end', () => resolve({ ok: true, status: res.statusCode }));
    });
    req.on('error', (err) => resolve({ ok: false, error: err.message }));
    req.setTimeout(3000, () => {
      req.destroy(new Error('timeout'));
    });
  });
}

let botBusy = false;
const bot = http.createServer(async (req, res) => {
  const u = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (u.pathname === '/bot') {
    return send(res, 200, `
<form action="/bot/run" method="GET">
  URL: <input name="url" placeholder="http://localhost:1337/" style="width: 400px;">
  <button>Run</button>
</form>
`, 'text/html; charset=utf-8');
  }

  if (u.pathname !== '/bot/run') return send(res, 404, 'not found');

  // These two console.log calls mirror the original admin.js behavior.
  console.log(FLAG);
  console.log(req.url);

  const targetUrl = u.searchParams.get('url');
  if (typeof targetUrl !== 'string' || !targetUrl.startsWith(`http://localhost:${WEB_PORT}`)) {
    return send(res, 200, 'invalid url');
  }
  if (botBusy) return send(res, 200, 'pls wait');

  botBusy = true;
  try {
    // The real bot creates this cookie in Chromium. For the local log-leak proof,
    // preserving the exact cookie string is enough to prove FLAG reaches document.cookie.
    const cookie = `flag${FLAG}`;
    await httpGet(targetUrl.replace('localhost', '127.0.0.1'));
    console.log(cookie);
  } finally {
    botBusy = false;
  }
  send(res, 200, 'ok');
});

web.listen(WEB_PORT, HOST, () => {
  console.error(`[+] web listening http://localhost:${WEB_PORT}/ root=${ROOT}`);
});
bot.listen(BOT_PORT, HOST, () => {
  console.error(`[+] bot listening http://localhost:${BOT_PORT}/bot`);
});

function shutdown() {
  web.close();
  bot.close();
}
process.on('SIGINT', () => { shutdown(); process.exit(0); });
process.on('SIGTERM', () => { shutdown(); process.exit(0); });
