const express = require('express')
const visit = require('./bot')

const PORT = process.env.PORT || 8000
const app = express()

app.use(express.urlencoded({ extended: false }))

app.post('/submit', async (req, res) => {
	const url = req.body.url
	if (!url || typeof url !== 'string') return res.status(400).send('Missing url')
	try {
		const u = new URL(url)
		if (u.protocol !== 'http:' && u.protocol !== 'https:') return res.status(400).send('Invalid protocol')
	} catch {
		return res.status(400).send('Invalid url')
	}
	console.log(`[+] Visiting ${url}`)
	res.send('OK')
	visit(url)
})

app.listen(PORT, () => console.log(`listening on :${PORT}`))
