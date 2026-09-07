import path from "path";
import { fileURLToPath } from "url";
import {
  getLlama,
  Llama3ChatWrapper,
  LlamaLogLevel,
  type Token,
  type ControlledEvaluateInputItem,
  type LlamaModel,
  type LlamaContextSequence,
} from "node-llama-cpp";
import type { Bit } from "./payload-bytes.ts";
import { bitsToPayloadBytes, payloadBytesToBits } from "./payload-bytes.ts";
import { logStegoDominant, logStegoEmbed } from "./stego-log.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * A factor to determine if the top non-EOG probability is dominant enough to be the only choice.
 * If we pick a token that is has probability way lower than the first, the output will seem unnatural.
 */
const DOMINANCE_FACTOR = 11;

/** A limit to prevent infinite loops. */
const MAX_STEGO_EMBED_STEPS = 500_000;

/**
 * Recover the same `completionTokens` array that `encrypt` used, from the exact
 * `completionText` produced by `detokenize(completionTokens, true, promptTokens)`.
 * Uses the same prefix window as `detokenize` (last N prompt tokens) so tokenization
 * aligns with how the completion string was formed.
 */
function completionTextToTokens(
  model: LlamaModel,
  promptTokens: readonly Token[],
  completionText: string
): Token[] {
  const n = Math.min(4, promptTokens.length);
  const addedTokens = promptTokens.slice(-n);
  const addedText = model.detokenize(addedTokens, true);
  const merged = addedText + completionText;
  const mergedTok = model.tokenize(merged, true);
  const prefixFromString = model.tokenize(addedText, true);

  const tryStrip = (prefix: readonly Token[]): Token[] | null => {
    if (mergedTok.length < prefix.length) return null;
    for (let i = 0; i < prefix.length; i++) {
      if (mergedTok[i] !== prefix[i]) return null;
    }
    return mergedTok.slice(prefix.length);
  };

  let completion = tryStrip(prefixFromString) ?? tryStrip(addedTokens);
  if (completion == null) {
    throw new Error(
      "Could not align tokenization: prefix of merged text does not match prompt tail. Use the exact completion string from encrypt()."
    );
  }

  const roundTrip = model.detokenize(completion, true, promptTokens);
  if (roundTrip !== completionText) {
    throw new Error(
      "Completion text does not round-trip to the same tokens as encrypt(); copy the exact string from encrypt()."
    );
  }
  return completion;
}

/** Non-EOG candidates sorted by probability desc, then token id asc. */
function getSortedNonEogEntries(
  probabilities: Map<Token, number>,
  isEogToken: (t: Token) => boolean
): [Token, number][] {
  const entries = [...probabilities.entries()].filter(([t]) => !isEogToken(t));
  entries.sort((a, b) => {
    const dp = b[1] - a[1];
    if (dp !== 0) return dp;
    return Number(a[0]) - Number(b[0]);
  });
  return entries as [Token, number][];
}

function isDominantOrOnlyChoice(
  sorted: readonly [Token, number][],
  factor: number = DOMINANCE_FACTOR
): boolean {
  if (sorted.length < 2) return true;
  const p0 = sorted[0]![1];
  const p1 = sorted[1]![1];
  if (p1 === 0) return true;
  return p0 >= factor * p1;
}

const generateNextBlock = {
  generateNext: {
    token: true as const,
    probabilities: true as const,
    options: { temperature: 0 as const },
  },
};

function withGenerateOnLast(
  tokens: readonly Token[]
): ControlledEvaluateInputItem[] {
  if (tokens.length === 0) throw new Error("Need at least one token");
  const items: ControlledEvaluateInputItem[] = tokens.slice(0, -1) as Token[];
  const last = tokens[tokens.length - 1] as Token;
  items.push([last, generateNextBlock]);
  return items;
}

function resolveModelPath(modelName: string): string {
  return path.join(__dirname, "..", "models", `${modelName}.gguf`);
}

async function withModel<T>(
  modelName: string,
  fn: (model: LlamaModel, sequence: LlamaContextSequence) => Promise<T>
): Promise<T> {
  const llama = await getLlama({ logLevel: LlamaLogLevel.error });
  const model = await llama.loadModel({
    modelPath: resolveModelPath(modelName),
  });
  const context = await model.createContext();
  try {
    const sequence = context.getSequence();
    return await fn(model, sequence);
  } finally {
    await context.dispose();
    await model.dispose();
  }
}

function promptTokensForUserMessage(
  model: LlamaModel,
  userPrompt: string
): Token[] {
  const chatWrapper = new Llama3ChatWrapper();
  const { contextText } = chatWrapper.generateContextState({
    chatHistory: [
      {
        type: "system",
        text: "You are a writing machine, when given an topic write about it for as long as possible. never offer to do anything else or add trailing questions. do not add any other text to the output. and do not interact with the user. do not add bits about being an assistant.",
      },
      { type: "user", text: userPrompt },
      /**
       * Empty assistant turn: puts `<|start_header_id|>assistant<|end_header_id|>\\n\\n` in the **prompt** so the model
       * does not spend tokens (and stego steps) emitting the role header before real output.
       */
      { type: "model", response: [] },
    ],
  });
  return contextText.tokenize(model.tokenizer);
}

export type EncryptOptions = {
  /** UTF-8 encoded for the bit stream (or pass raw bytes). */
  payload: string | Uint8Array;
  modelName: string;
  userPrompt: string;
};

export type EncryptResult = {
  completionText: string;
  completionTokens: Token[];
};

export async function encrypt(options: EncryptOptions): Promise<EncryptResult> {
  const bytes =
    typeof options.payload === "string"
      ? new TextEncoder().encode(options.payload)
      : options.payload;
  const bitStream = payloadBytesToBits(bytes);

  return withModel(options.modelName, async (model, sequence) => {
    const promptTokens = promptTokensForUserMessage(model, options.userPrompt);
    const completionTokens: Token[] = [];
    let evaluateInput: ControlledEvaluateInputItem[] =
      withGenerateOnLast(promptTokens);

    let bitIndex = 0;
    let embedStep = 0;
    while (bitIndex < bitStream.length) {
      if (++embedStep > MAX_STEGO_EMBED_STEPS) {
        throw new Error(
          "llm-steganography: exceeded max generation steps while embedding (try lowering DOMINANCE_FACTOR or changing the prompt)"
        );
      }
      const result = await sequence.controlledEvaluate(evaluateInput);
      const idx = evaluateInput.length - 1;
      const probs = result[idx]?.next?.probabilities;
      if (!probs) throw new Error("No probabilities returned");

      const sorted = getSortedNonEogEntries(probs, (t) => model.isEogToken(t));
      if (sorted.length === 0) {
        throw new Error("No non-EOG candidates in the distribution");
      }

      let chosen: Token;
      if (isDominantOrOnlyChoice(sorted)) {
        logStegoDominant(model, sorted[0]!);
        chosen = sorted[0]![0];
      } else {
        logStegoEmbed(model, [sorted[0]!, sorted[1]!], bitStream[bitIndex]!);
        const pair: [Token, Token] = [sorted[0]![0], sorted[1]![0]];
        chosen = pair[bitStream[bitIndex]!]!;
        bitIndex++;
      }

      completionTokens.push(chosen);
      evaluateInput = [[chosen, generateNextBlock]];
    }

    const completionText = model.detokenize(
      completionTokens,
      true,
      promptTokens
    );
    return { completionText, completionTokens };
  });
}

/** Exact string returned by `encrypt` as `completionText` (same model + userPrompt). */
export type DecryptOptions = {
  completionText: string;
  modelName: string;
  userPrompt: string;
};

export async function decrypt(options: DecryptOptions): Promise<string> {
  const { completionText, modelName, userPrompt } = options;
  return withModel(modelName, async (model, sequence) => {
    const promptTokens = promptTokensForUserMessage(model, userPrompt);
    const completionTokens = completionTextToTokens(
      model,
      promptTokens,
      completionText
    );
    const bits: Bit[] = [];
    let evaluateInput: ControlledEvaluateInputItem[] =
      withGenerateOnLast(promptTokens);

    for (let i = 0; i < completionTokens.length; i++) {
      const result = await sequence.controlledEvaluate(evaluateInput);
      const idx = evaluateInput.length - 1;
      const probs = result[idx]?.next?.probabilities;
      if (!probs) throw new Error("No probabilities returned");

      const sorted = getSortedNonEogEntries(probs, (t) => model.isEogToken(t));
      const token = completionTokens[i]!;
      if (sorted.length === 0) {
        throw new Error("No non-EOG candidates when decoding");
      }

      if (isDominantOrOnlyChoice(sorted)) {
        if (token !== sorted[0]![0]) {
          throw new Error(
            "Completion token does not match forced top candidate"
          );
        }
      } else {
        const pair: [Token, Token] = [sorted[0]![0], sorted[1]![0]];
        if (token === pair[0]) bits.push(0);
        else if (token === pair[1]) bits.push(1);
        else {
          throw new Error(
            "Completion token does not match top-2 candidate pair"
          );
        }
      }

      evaluateInput = [[token, generateNextBlock]];
    }

    const raw = bitsToPayloadBytes(bits);
    return new TextDecoder().decode(raw);
  });
}
