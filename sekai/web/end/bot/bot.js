const puppeteer = require('puppeteer')

const SITE = process.env.SITE || 'http://proxy:3000'
const ADMIN_TOKEN = process.env.ADMIN_TOKEN

const sleep = async ms => new Promise(resolve => setTimeout(resolve, ms))

const CHROME_ARGS = [
	'--no-sandbox',
	'--js-flags=--jitless,--no-expose-wasm',
	'--disable-gpu',
	'--disable-dev-shm-usage',
	'--disable-popup-blocking'
]

function buildSecureOrigins(submittedUrl) {
	const origins = new Set()
	origins.add(SITE)

	try {
		const u = new URL(submittedUrl)
		if (u.protocol === 'http:') origins.add(u.origin)
	} catch {}

	return [...origins]
}

const visit = async url => {
	let browser = null
	try {
		const secureOrigins = buildSecureOrigins(url)
		const args = [...CHROME_ARGS]
		const httpOrigins = secureOrigins.filter(u => {
			try { return new URL(u).protocol === 'http:' } catch { return false }
		})
		if (httpOrigins.length) {
			args.push(`--unsafely-treat-insecure-origin-as-secure=${httpOrigins.join(',')}`)
		}

		browser = await puppeteer.launch({ headless: 'new', args })

		const page = await browser.newPage()
		const siteUrl = new URL(SITE)
		await page.setCookie({
			name: 'session',
			value: ADMIN_TOKEN,
			domain: siteUrl.hostname,
			path: '/',
			httpOnly: true,
			sameSite: 'Lax'
		})

		await Promise.race([
			page.goto(url, { waitUntil: 'networkidle0' }),
			sleep(15000)
		])
		await sleep(120000)
	} catch (e) {
		console.log(e)
	} finally {
		if (browser) await browser.close()
	}
}

module.exports = visit
