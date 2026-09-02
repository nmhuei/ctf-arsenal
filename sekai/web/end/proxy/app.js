const http = require('http')
const https = require('https')
const crypto = require('crypto')
const dns = require('dns')
const fs = require('fs')
const path = require('path')

const PORT = process.env.PORT || 3000
const TOKEN = process.env.ADMIN_TOKEN || crypto.randomUUID()
const API_URL = process.env.API_URL || 'http://api:9090'
const API_KEY = process.env.API_KEY || ''

const CSP = [
	"default-src 'self'",
	"script-src 'self'",
	"style-src 'unsafe-inline' *",
	"img-src *",
	"font-src *",
	"frame-src 'self'",
	"object-src 'none'",
	"base-uri 'self'",
	"form-action 'self'",
	"worker-src 'self'",
	"frame-ancestors 'self'"
].join('; ')

const MIME = {
	'.js': 'application/javascript',
	'.css': 'text/css'
}

const INDEX_HTML = fs.readFileSync(path.join(__dirname, 'static', 'index.html'), 'utf8')
const ADMIN_HTML = fs.readFileSync(path.join(__dirname, 'static', 'admin.html'), 'utf8')

const pages = new Map()

const defaults = {
	nodejs: 'https://nodejs.org/docs/latest/api/',
	mdn: 'https://developer.mozilla.org/en-US/',
	python: 'https://docs.python.org/3/',
	golang: 'https://go.dev/doc/'
}

for (const [name, url] of Object.entries(defaults)) {
	pages.set(name, { url })
}

function checkAuth(req) {
	for (const part of (req.headers.cookie || '').split(';')) {
		const [k, ...v] = part.split('=')
		if (k.trim() === 'session' && v.join('=').trim() === TOKEN) return true
	}
	return false
}

function respond(res, code, type, body) {
	res.writeHead(code, {
		'content-type': type,
		'content-security-policy': CSP,
		'x-content-type-options': 'nosniff'
	})
	res.end(body)
}

function esc(s) {
	return s
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;')
}

function isPrivateIP(addr) {
	if (!addr) return true
	const ip = String(addr).toLowerCase().trim()

	if (ip.includes(':')) {
		if (ip === '::' || ip === '::1') return true
		if (ip.startsWith('fe80') || ip.startsWith('fc') || ip.startsWith('fd')) return true
		const mapped = ip.match(/(?:::ffff:)(\d+\.\d+\.\d+\.\d+)$/)
		if (mapped) return isPrivateIP(mapped[1])
		const hexMapped = ip.match(/::ffff:([0-9a-f]{1,4}):([0-9a-f]{1,4})$/)
		if (hexMapped) {
			const a = parseInt(hexMapped[1], 16), b = parseInt(hexMapped[2], 16)
			return isPrivateIP(`${a >> 8}.${a & 255}.${b >> 8}.${b & 255}`)
		}
		return false
	}

	const parts = ip.split('.')
	if (parts.length !== 4) return true
	const o = parts.map(p => Number(p))
	if (o.some(n => !Number.isInteger(n) || n < 0 || n > 255)) return true
	const [a, b] = o
	if (a === 0 || a === 10 || a === 127) return true
	if (a === 169 && b === 254) return true
	if (a === 172 && b >= 16 && b <= 31) return true
	if (a === 192 && b === 168) return true
	if (a === 100 && b >= 64 && b <= 127) return true
	return false
}

function isPublicHostname(parsed) {
	const h = parsed.hostname.replace(/\.+$/, '')
	if (!h.includes('.')) return false
	if (/^(127\.|10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.|0\.|169\.254\.|100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.)/.test(h)) return false
	if (h === 'localhost' || h.startsWith('localhost.')) return false
	return true
}

function renderIndex() {
	const items = [...pages]
		.map(([n, p]) => {
			const d = p.desc ? ` &mdash; ${esc(p.desc)}` : ''
			return `<li><a href="/view/${n}/">${n}</a>${d}</li>`
		})
		.join('\n')

	return INDEX_HTML.replace('{{PAGES}}', items || '<li>No pages yet</li>')
}

function renderAdmin() {
	const items = [...pages]
		.map(([n]) => `<li><a href="/view/${n}/">${n}</a></li>`)
		.join('\n')

	return ADMIN_HTML
		.replace('{{PAGES}}', items || '<li>none</li>')
		.replace('{{API_URL}}', esc(API_URL))
		.replace('{{API_KEY}}', esc(API_KEY))
}

function proxyTo(origin, req, res) {
	const target = new URL(req.url, origin)
	const expected = new URL(origin)
	const mod = target.protocol === 'https:' ? https : http

	if (target.hostname !== expected.hostname) {
		return respond(res, 403, 'text/plain', 'Blocked')
	}

	dns.lookup(target.hostname, { all: false }, (err, address) => {
		if (err) return respond(res, 502, 'text/plain', 'upstream error')
		if (isPrivateIP(address)) {
			return respond(res, 403, 'text/plain', 'Blocked')
		}

		delete req.headers.host
		delete req.headers.cookie
		delete req.headers.referer

		const opts = {
			hostname: address,
			port: target.port || (target.protocol === 'https:' ? 443 : 80),
			path: target.pathname + target.search,
			method: req.method,
			headers: { ...req.headers, host: target.host }
		}
		if (target.protocol === 'https:') opts.servername = target.hostname

		const proxyReq = mod.request(opts, proxyRes => {
			const h = { ...proxyRes.headers }

			h['content-security-policy'] = CSP
			h['x-content-type-options'] = 'nosniff'
			if (!h['content-type']) h['content-type'] = 'text/plain'
			delete h['cache-control']
			delete h['etag']
			delete h['expires']
			h['cache-control'] = 'no-store'

			if (req.headers['sec-fetch-dest'] === 'script') {
				h['content-length'] = '0'
				delete h['transfer-encoding']
			}

			res.writeHead(proxyRes.statusCode, proxyRes.statusMessage, h)
			proxyRes.pipe(res)
		})

		req.pipe(proxyReq)
		proxyReq.on('error', () => {
			try { respond(res, 502, 'text/plain', 'upstream error') } catch {}
		})
	})
}

http.createServer((req, res) => {
	const url = new URL(req.url, 'http://localhost')

	if (url.pathname.startsWith('/static/')) {
		const file = path.basename(url.pathname.slice(8))
		if (!file || file.startsWith('.') || file.includes('..')) {
			return respond(res, 404, 'text/plain', 'Not found')
		}
		const ext = path.extname(file)
		if (!MIME[ext]) return respond(res, 404, 'text/plain', 'Not found')
		try {
			const data = fs.readFileSync(path.join(__dirname, 'static', file))
			return respond(res, 200, MIME[ext], data)
		} catch {
			return respond(res, 404, 'text/plain', 'Not found')
		}
	}

	if (url.pathname === '/') {
		return respond(res, 200, 'text/html', renderIndex())
	}

	if (url.pathname === '/admin') {
		if (!checkAuth(req)) return respond(res, 403, 'text/plain', 'Forbidden')
		return respond(res, 200, 'text/html', renderAdmin())
	}

	if (url.pathname === '/add') {
		const name = url.searchParams.get('name')
		const site = url.searchParams.get('url')
		const desc = (url.searchParams.get('desc') || '').slice(0, 200)

		if (!name || !site) return respond(res, 400, 'text/plain', 'Missing parameters')
		if (!/^[a-z0-9]{4,32}$/.test(name)) return respond(res, 400, 'text/plain', 'Invalid name')

		let parsed
		try { parsed = new URL(site) } catch {
			return respond(res, 400, 'text/plain', 'Invalid URL')
		}

		if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
			return respond(res, 400, 'text/plain', 'Only http/https allowed')
		}

		if (!isPublicHostname(parsed)) {
			return respond(res, 400, 'text/plain', 'Only public URLs allowed')
		}

		if (pages.has(name)) return respond(res, 409, 'text/plain', 'Name taken')

		pages.set(name, { url: parsed.href, desc })
		return respond(res, 201, 'text/plain', `/view/${name}/`)
	}

	const m = url.pathname.match(/^\/view\/([a-z0-9]+)\/(.*)$/)
	if (m) {
		const entry = pages.get(m[1])
		if (!entry) return respond(res, 404, 'text/plain', 'Not found')
		req.url = '/' + m[2].replace(/^\/+/, '') + url.search
		return proxyTo(entry.url, req, res)
	}

	if (/^\/view\/[a-z0-9]+$/.test(url.pathname)) {
		res.writeHead(302, { location: url.pathname + '/' })
		return res.end()
	}

	respond(res, 404, 'text/plain', 'Not found')

}).listen(PORT, () => console.log(`listening on :${PORT}`))
