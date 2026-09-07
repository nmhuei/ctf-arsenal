#!/usr/bin/env bun
import { readFile, writeFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
import { Command } from "commander";
import { decrypt, encrypt } from "./stego.ts";

const pkg = JSON.parse(
  readFileSync(new URL("../package.json", import.meta.url), "utf8")
) as { version: string; name: string };

async function readStdinUtf8(): Promise<string> {
  const chunks: Uint8Array[] = [];
  const reader = Bun.stdin.stream().getReader();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if (value) chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  return new TextDecoder().decode(Buffer.concat(chunks));
}

async function main() {
  const program = new Command();
  program
    .name(pkg.name)
    .description("LLM output steganography (embed a payload in token choices)")
    .version(pkg.version);

  program
    .command("encrypt")
    .description("Embed a secret into generated completion text")
    .requiredOption(
      "-u, --user-prompt <string>",
      "user instruction (same for decrypt)"
    )
    .option("-p, --payload <string>", "UTF-8 payload string")
    .option("-P, --payload-file <path>", "read payload from file")
    .option("-m, --model <name>", "GGUF basename under models/", "llama3")
    .option(
      "-o, --output <file>",
      "write completion text to file (default: stdout)"
    )
    .action(
      async (opts: {
        userPrompt: string;
        payload?: string;
        payloadFile?: string;
        model: string;
        output?: string;
      }) => {
        const hasPayload = opts.payload !== undefined;
        const hasPayloadFile = opts.payloadFile !== undefined;
        if (hasPayload === hasPayloadFile) {
          program.error(
            "encrypt: use exactly one of --payload or --payload-file"
          );
        }
        const payload = hasPayloadFile
          ? await readFile(opts.payloadFile!, "utf8")
          : opts.payload!;
        const { completionText } = await encrypt({
          payload,
          modelName: opts.model,
          userPrompt: opts.userPrompt,
        });
        if (opts.output) {
          await writeFile(opts.output, completionText, "utf8");
        } else {
          // No trailing newline: decrypt requires byte-for-byte match with encrypt output.
          process.stdout.write(completionText);
        }
      }
    );

  program
    .command("decrypt")
    .description("Recover the payload from completion text")
    .requiredOption("-u, --user-prompt <string>", "same user prompt as encrypt")
    .option(
      "-f, --file <path>",
      "file with exact completion text (use - for stdin)"
    )
    .option("-m, --model <name>", "GGUF basename under models/", "llama3")
    .option("-o, --output <file>", "write payload to file (default: stdout)")
    .action(
      async (opts: {
        userPrompt: string;
        file?: string;
        model: string;
        output?: string;
      }) => {
        let completionText: string;
        if (opts.file === "-") {
          completionText = await readStdinUtf8();
        } else if (opts.file) {
          completionText = await readFile(opts.file, "utf8");
        } else if (process.stdin.isTTY) {
          program.error(
            "decrypt: pass --file <path>, --file - for stdin, or pipe completion text on stdin"
          );
          return;
        } else {
          completionText = await readStdinUtf8();
        }
        const payload = await decrypt({
          completionText,
          modelName: opts.model,
          userPrompt: opts.userPrompt,
        });
        if (opts.output) {
          await writeFile(opts.output, payload, "utf8");
        } else {
          process.stdout.write(payload);
        }
      }
    );

  await program.parseAsync(process.argv);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
