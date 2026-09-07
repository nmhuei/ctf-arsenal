import { describe, expect, test } from "bun:test";
import { encrypt, decrypt } from "./stego.ts";

describe("encrypt / decrypt", () => {
  test(
    "round-trip",
    async () => {
      const userPrompt = "Write a pasta recipe.";
      const payload = "hello world";
      const { completionText } = await encrypt({
        payload,
        modelName: "llama3",
        userPrompt,
      });
      const out = await decrypt({
        completionText,
        modelName: "llama3",
        userPrompt,
      });
      expect(out).toBe(payload);
    },
    { timeout: 300_000 }
  );
});
