// NODE_ENV=production node --disallow-code-generation-from-strings chal.js
import { createInterface } from "node:readline/promises";
import jail from "./jail.js";

/* 😇😇😇 */
process.env.NODE_ENV !== "production" && process.reallyExit(1);

try {
  Function();
  process.reallyExit(1);
} catch {}

/* 😇😇😇 */

using rl = createInterface(process.stdin, process.stdout);

const b64flight = await rl.question("flight (b64): ");

try {
  var flight = atob(b64flight);
} catch {
  process.reallyExit(1);
}

// flight.length >= 600 && process.reallyExit(1); // <--- + 1 golf tag
flight.length >= 1500 && process.reallyExit(1); // <--- no golf tag

await jail(flight);
