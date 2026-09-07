import type { LlamaModel, Token } from "node-llama-cpp";
import type { Bit } from "./payload-bytes.ts";

export type StegoLogLevel = "debug" | null;

/** Set to `"debug"` for colored encrypt-step logs; `null` to silence. */
export const STEGO_LOG_LEVEL: StegoLogLevel = null;

function colorsEnabled(): boolean {
  return (
    typeof process !== "undefined" &&
    Boolean(process.stdout?.isTTY) &&
    !process.env.NO_COLOR &&
    !process.env.NO_COLOUR
  );
}

function style() {
  const on = colorsEnabled();
  const s = (code: string, text: string) =>
    on ? `\x1b[${code}m${text}\x1b[0m` : text;
  return {
    bold: (t: string) => s("1", t),
    cyan: (t: string) => s("36", t),
    green: (t: string) => s("32", t),
    yellow: (t: string) => s("33", t),
  };
}

function preview(model: LlamaModel, token: Token): string {
  return `"${model.tokenizer.detokenize([token]).replace(/\n/g, "\\n")}"`;
}

export function logStegoDominant(
  model: LlamaModel,
  entry: [Token, number]
): void {
  if (STEGO_LOG_LEVEL !== "debug") return;
  const { bold, cyan, green } = style();
  const [token, p] = entry;
  console.log(
    `${bold("dominant")}  ${green(p.toFixed(4))} ${cyan(preview(model, token))}`
  );
}

function logStegoEmbedOption(
  model: LlamaModel,
  tokenEntry: [Token, number]
): string {
  const { green, cyan } = style();
  const [token, prob] = tokenEntry;
  return `${green(prob.toFixed(4))} ${cyan(preview(model, token))}`.padEnd(
    40,
    " "
  );
}

export function logStegoEmbed(
  model: LlamaModel,
  topTwo: readonly [[Token, number], [Token, number]],
  bit: Bit
): void {
  if (STEGO_LOG_LEVEL !== "debug") return;
  const { bold, yellow } = style();
  const [a, b] = topTwo;
  console.log(
    `${bold("embed")}     ` +
      `${logStegoEmbedOption(model, a)} or ${logStegoEmbedOption(model, b)}` +
      `${yellow(`picking bit=${bit}`)} `
  );
}
