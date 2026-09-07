const { getBotCredentials } = require("../services/databaseInitialization");

const intervalMs = 60 * 1000;
let botTimer;

async function launchBrowser() {
  const puppeteerModule = await import("puppeteer");
  const puppeteer = puppeteerModule.default || puppeteerModule;
  const options = {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  };

  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    options.executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
  }

  return puppeteer.launch(options);
}

async function login(page, baseUrl, username, password) {
  await page.goto(baseUrl, { waitUntil: "networkidle0" });
  await page.waitForSelector('form[action="/login"]');
  await page.type('input[name="username"]', username);
  await page.type('input[name="password"]', password);
  await Promise.all([
    page.waitForNavigation({ waitUntil: "networkidle0" }),
    page.click('form[action="/login"] button[type="submit"]'),
  ]);

  if (new URL(page.url()).pathname !== "/chat") {
    throw new Error(`Unable to log in as ${username}.`);
  }
}

async function findConversation(page, username) {
  return page.$$eval(
    ".conversation",
    (conversations, expectedUsername) => {
      const conversation = conversations.find(
        (item) =>
          item.querySelector("strong")?.textContent.trim() === expectedUsername
      );
      if (!conversation) return null;

      return {
        href: conversation.href,
        preview:
          conversation
            .querySelector(".conversation-copy span")
            ?.textContent.trim() || "",
      };
    },
    username
  );
}

async function visitAsHacker(baseUrl, password) {
  const browser = await launchBrowser();
  try {
    const page = await browser.newPage();
    await login(page, baseUrl, "Hacker", password);

    const conversation = await findConversation(page, "FlagHolder");
    if (!conversation)
      throw new Error("FlagHolder conversation was not found.");

    await page.goto(conversation.href, { waitUntil: "networkidle0" });
    await new Promise((resolve) => setTimeout(resolve, 3000));
  } finally {
    await browser.close();
  }
}

async function replyAsFlagHolder(baseUrl, password, flag) {
  const browser = await launchBrowser();
  try {
    const page = await browser.newPage();
    await login(page, baseUrl, "FlagHolder", password);

    const conversation = await findConversation(page, "Hacker");
    if (!conversation || conversation.preview !== "Give me the flag!") return;

    await page.goto(conversation.href, { waitUntil: "networkidle0" });
    await page.waitForSelector("#message-input");
    await page.type("#message-input", flag);
    await Promise.all([
      page.waitForNavigation({ waitUntil: "networkidle0" }),
      page.click('.composer button[type="submit"]'),
    ]);
  } finally {
    await browser.close();
  }
}

async function runBotCycle(baseUrl) {
  const credentials = getBotCredentials();
  if (!process.env.FLAG) throw new Error("FLAG is not configured.");

  await visitAsHacker(baseUrl, credentials.Hacker);
  await replyAsFlagHolder(baseUrl, credentials.FlagHolder, process.env.FLAG);
}

function startBot(baseUrl) {
  if (botTimer) return botTimer;
  let running = false;

  const run = async () => {
    if (running) return;
    running = true;
    try {
      await runBotCycle(baseUrl);
    } catch (error) {
      console.error(`Bot cycle failed: ${error.message}`);
    } finally {
      running = false;
    }
  };

  void run();
  botTimer = setInterval(run, intervalMs);
  return botTimer;
}

module.exports = { findConversation, login, runBotCycle, startBot };
