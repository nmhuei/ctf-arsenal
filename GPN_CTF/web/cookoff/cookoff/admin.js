
let app = require('express')()
let { chromium } = require('playwright')

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms))
}


let botBusy = false

app.get('/bot', (req, res) => res.send(`
    <form action="/bot/run" method="GET">
        URL: <input name="url" placeholder="http://localhost:1337/" style="width: 400px;">
        <button>Run</button>
    </form>
`))

app.get('/bot/run', async (req, res) => {
    console.log(process.env.FLAG)
console.log(req.url)
    const targetUrl = req.query.url
    if (typeof targetUrl === 'string' && !targetUrl.startsWith('http://localhost:1337')) {
        return res.send('invalid url')
    }

    if (!botBusy) {
        botBusy = true
        try {
            let browser
            const launchOptions = {
                headless: true
            }

            browser = await chromium.launch(launchOptions)

            
            const page = await browser.newPage()
            await page.goto("http://localhost:1337")
            await page.evaluate(flag => document.cookie = "flag"+flag, process.env.FLAG)
            await page.goto(targetUrl, {
                waitUntil: 'domcontentloaded',
                timeout: 15000
            })
            await sleep(10000)
                        console.log(await page.evaluate(()=> document.cookie))

            await browser.close()
        } catch (err) {
            console.error(err)
        } finally {
            botBusy = false
        }
    } else {
        return res.send('pls wait')
    }

    return res.send('ok')
})

app.listen(8080)
