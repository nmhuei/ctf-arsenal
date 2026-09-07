require("dotenv").config();

const fs = require("fs");
const path = require("path");
const express = require("express");
const cookieParser = require("cookie-parser");
const { loadUser } = require("./middleware/auth");
const { errorHandler, notFound } = require("./middleware/errorHandler");
const { initializeDatabase } = require("./services/databaseInitialization");
const { messageMarkup } = require("./services/messageMarkup");
const { startBot } = require("./bot");

const app = express();
const configuredPort = Number(process.env.PORT);
const port = Number.isInteger(configuredPort) ? configuredPort : 3000;

fs.mkdirSync(path.join(__dirname, "data"), { recursive: true });

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.disable("x-powered-by");

app.use((_req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval'",
      "script-src-elem 'self'",
      "script-src-attr 'unsafe-inline'",
      "object-src 'none'",
      "base-uri 'none'",
    ].join("; ")
  );
  next();
});

app.use(express.urlencoded({ extended: false, limit: "6mb" }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "public")));
app.use(loadUser);
app.use((req, res, next) => {
  res.locals.notice = req.query.notice || null;
  res.locals.error = req.query.error || null;
  res.locals.form = {};
  res.locals.path = req.path;
  res.locals.formatTime = (date) =>
    new Intl.DateTimeFormat("en", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(date));
  res.locals.messageMarkup = messageMarkup;
  next();
});

app.get("/", (req, res) => res.redirect(req.user ? "/chat" : "/login"));
app.use(require("./routes/auth"));
app.use(require("./routes/users"));
app.use(require("./routes/friends"));
app.use(require("./routes/messages"));
app.use(require("./routes/settings"));
app.use(notFound);
app.use(errorHandler);

async function start() {
  await initializeDatabase();
  return new Promise((resolve, reject) => {
    const server = app.listen(port, "0.0.0.0", (error) => {
      if (error) {
        reject(error);
        return;
      }

      const address = server.address();
      if (!address) {
        reject(
          new Error("The HTTP server closed before it finished starting.")
        );
        return;
      }

      const actualPort = address.port;
      console.log(`Tagger is online at http://localhost:${actualPort}`);

      startBot(`http://127.0.0.1:${actualPort}`);

      resolve(server);
    });
  });
}

if (require.main === module) {
  start().catch((error) => {
    console.error("Unable to start Tagger:", error);
    process.exit(1);
  });
}

module.exports = { app, start };
