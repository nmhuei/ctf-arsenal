// https://nextjs.org/docs/app/guides/custom-server

import next from "next";
import { createServer } from "http";

const port = parseInt(process.env.PORT || "3000");

process.env.NODE_ENV = "production";

const app = next({
  minimalMode: true,
  customServer: false, // <--- gift for u
});
const handle = app.getRequestHandler();

app.prepare().then(() => {
  createServer(async (req, res) => {
    try {
      await handle(req, res);
    } catch (error) {
      console.log("error?!", error);
      if (!res.headersSent) res.writeHead(500);
      res.end("meow?");
    }
  }).listen(port);

  console.log(`> Server listening at http://localhost:${port}`);
});
