import { decrypt, encrypt } from "./stego.ts";
import { payloadBytesToBits } from "./payload-bytes.ts";

const userPrompt = "a pizza recepie";
const payload = "hello";

console.log("userPrompt:", userPrompt);
console.log("payload:", payload);

const payloadBits = payloadBytesToBits(new TextEncoder().encode(payload));
console.log("payload bits:", payloadBits);

const { completionText } = await encrypt({
  payload,
  modelName: "llama3",
  userPrompt,
});

console.log({
  completionText: completionText.replaceAll(/\s+/g, " "),
});

const decoded = await decrypt({
  completionText,
  modelName: "llama3",
  userPrompt,
});

console.log("decrypted:", JSON.stringify(decoded));
console.log("ok:", decoded === payload);
