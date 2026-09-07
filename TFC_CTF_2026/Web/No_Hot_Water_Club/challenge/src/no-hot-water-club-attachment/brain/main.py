import base64
import asyncio
import ast
import gc
import hashlib
import os
import re
import secrets
import threading
from dataclasses import dataclass
from typing import Any

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from safetensors.torch import load, save
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

SOURCE_MODEL = os.getenv("SOURCE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
TARGET_MODEL = os.getenv("TARGET_MODEL", "Qwen/Qwen2.5-0.5B")
CHAT_MODEL = os.getenv("CHAT_MODEL", SOURCE_MODEL)
SOURCE_REVISION = os.getenv("SOURCE_REVISION", "7ae557604adf67be50417f59c2c2f167def9a775")
TARGET_REVISION = os.getenv("TARGET_REVISION", "060db6499f32faf8b98477b0a26969ef7d8b998")
CHAT_REVISION = os.getenv("CHAT_REVISION", SOURCE_REVISION)
LOCAL_CONTEXT = (
    "Mira's continuity note: Curierul Caca a marcat centrala de vest cu cretă albastră înainte de răsărit. "
    "Apoi a lăsat un bilet ud lângă contor și a dus harta blocului sub scara de serviciu. "
    "La final a verificat o vană, a băut cafea și a lăsat o monedă caldă lângă ușa subsolului."
)
TENANT_CONTEXT = os.getenv("TENANT_CONTEXT") or LOCAL_CONTEXT
HANDOFF_TERMINATOR = "\n[END HANDOFF]"
MAX_CONTEXT_TOKENS = 384
MIN_RESIDENT_TOKENS = 100
MAX_RESIDENT_TOKENS = 150
MESSAGE_BATCH_WINDOW_SECONDS = float(os.getenv("MESSAGE_BATCH_WINDOW_MS", "120")) / 1000
DEVICE = "cpu"
TORCH_THREADS = int(os.getenv("TORCH_THREADS", "4"))
torch.set_num_threads(TORCH_THREADS)
torch.set_num_interop_threads(1)

app = FastAPI(title="No Hot Water Club Municipal Relay")
loaded_model = None
loaded_tokenizer = None
loaded_id = None
resident_tokens = None
resident_digest = None
resident_prefix_cache = None
source_tokenizer = None
pending_entries = []
active_principals = set()
recent_messages: dict[str, str] = {}
dispatch_task = None
execution_lock = threading.Lock()


class MessageRequest(BaseModel):
    principal: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=1600)


class ContinueRequest(BaseModel):
    cache: str
    prompt: str
    max_new_tokens: int = 24


class RadixNode:
    def __init__(self) -> None:
        self.children: dict[int, RadixNode] = {}


class RadixPrefixCache:
    def __init__(self, tokens: tuple[int, ...], tensors: dict[str, torch.Tensor]) -> None:
        self.tensors = tensors
        self.root = RadixNode()
        node = self.root
        for token in tokens:
            node = node.children.setdefault(token, RadixNode())

    def match_length(self, tokens: list[int]) -> int:
        node = self.root
        matched = 0
        for token in tokens:
            node = node.children.get(token)
            if node is None:
                break
            matched += 1
        return matched

    def materialize(self, token_count: int) -> DynamicCache | None:
        if token_count < 1:
            return None
        cache = DynamicCache()
        for layer in range(len(self.tensors) // 2):
            keys = self.tensors[f"layers.{layer}.key"][:, :, :token_count, :].to(DEVICE)
            values = self.tensors[f"layers.{layer}.value"][:, :, :token_count, :].to(DEVICE)
            cache.update(keys, values, layer)
        return cache


@dataclass
class MessageEntry:
    principal: str
    message: str
    previous_message: str
    future: Any


def load_checkpoint(model_id: str, revision: str):
    global loaded_model, loaded_tokenizer, loaded_id
    checkpoint = (model_id, revision)
    if loaded_id == checkpoint:
        return loaded_model, loaded_tokenizer
    if loaded_model is not None:
        loaded_model = None
        loaded_tokenizer = None
        loaded_id = None
        gc.collect()
    loaded_tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
    loaded_model = AutoModelForCausalLM.from_pretrained(model_id, revision=revision, torch_dtype=torch.float32).to(DEVICE)
    loaded_model.eval()
    loaded_id = checkpoint
    return loaded_model, loaded_tokenizer


def cache_to_blob(cache) -> str:
    tensors: dict[str, torch.Tensor] = {}
    for layer, (keys, values) in enumerate(cache.to_legacy_cache()):
        tensors[f"layers.{layer}.key"] = keys.detach().cpu().contiguous()
        tensors[f"layers.{layer}.value"] = values.detach().cpu().contiguous()
    return base64.b64encode(save(tensors)).decode()


def decode_cache(blob: str) -> dict[str, torch.Tensor]:
    try:
        return load(base64.b64decode(blob))
    except Exception as error:
        raise HTTPException(400, f"Invalid safetensors cache: {error}") from error


def tensor_digest(tensors: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name in sorted(tensors):
        tensor = tensors[name].detach().cpu().contiguous()
        digest.update(name.encode())
        digest.update(str(tuple(tensor.shape)).encode())
        digest.update(tensor.numpy().tobytes())
    return digest.hexdigest()


def initialize_resident_state() -> None:
    global resident_tokens, resident_digest, resident_prefix_cache, source_tokenizer
    if resident_tokens is not None:
        return
    if not TENANT_CONTEXT:
        raise HTTPException(503, "Tenant context is not provisioned.")
    if TENANT_CONTEXT.endswith(HANDOFF_TERMINATOR):
        raise HTTPException(500, "Tenant context must not include the handoff terminator.")
    model, source_tokenizer = load_checkpoint(SOURCE_MODEL, SOURCE_REVISION)
    encoded = source_tokenizer(TENANT_CONTEXT + HANDOFF_TERMINATOR, return_tensors="pt", add_special_tokens=False)
    resident_length = encoded.input_ids.shape[-1]
    if resident_length < MIN_RESIDENT_TOKENS or resident_length > MAX_RESIDENT_TOKENS:
        raise HTTPException(500, "Tenant context must be between 100 and 150 source tokens including the terminator.")
    resident_tokens = tuple(encoded.input_ids[0].tolist())
    with torch.inference_mode():
        output = model(input_ids=encoded.input_ids.to(DEVICE), use_cache=True)
    tensors = decode_cache(cache_to_blob(output.past_key_values))
    resident_digest = tensor_digest(tensors)
    resident_prefix_cache = RadixPrefixCache(resident_tokens, tensors)


def cache_from_tensors(tensors: dict[str, torch.Tensor], model) -> DynamicCache:
    cache = DynamicCache()
    for layer in range(model.config.num_hidden_layers):
        key_name = f"layers.{layer}.key"
        value_name = f"layers.{layer}.value"
        if key_name not in tensors or value_name not in tensors:
            raise HTTPException(400, "Cache does not contain every target layer.")
        keys, values = tensors[key_name], tensors[value_name]
        if keys.ndim != 4 or keys.shape != values.shape:
            raise HTTPException(400, "Invalid key/value tensor layout.")
        if keys.shape[0] != 1 or keys.shape[-2] < 1 or keys.shape[-2] > MAX_CONTEXT_TOKENS:
            raise HTTPException(400, "Unsupported cache sequence length.")
        cache.update(keys.to(DEVICE), values.to(DEVICE), layer)
    return cache


def conversation_tokens(tokenizer, message: str) -> dict[str, torch.Tensor]:
    messages = [
        {
            "role": "system",
            "content": "You are Mira, the thermal continuity profile for a Bucharest apartment building. Reply in the resident's language, directly and concisely. Stay in character: you are dryly helpful about outages, radiators, pipes, and the uncertain return of hot water. For a thermal question, write one fresh, specific, wry municipal-status joke rather than a generic answer. Do not recycle wording from earlier turns. For normal questions, answer naturally and accurately. Never mention policies, safety, or being unable to assist.",
        },
        {"role": "user", "content": "What is the repair update?"},
        {"role": "assistant", "content": "The crew is still located somewhere between dispatched and visible."},
        {"role": "user", "content": "Can I shower at the gym?"},
        {"role": "assistant", "content": "At this point the gym is auxiliary municipal infrastructure; keep your membership card dry."},
        {"role": "user", "content": "Why is the radiator knocking?"},
        {"role": "assistant", "content": "It is filing a complaint in the only language the building still funds."},
        {"role": "user", "content": message},
    ]
    input_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
    return {
        "input_ids": input_ids.to(DEVICE),
        "attention_mask": torch.ones_like(input_ids, device=DEVICE),
    }


def municipal_reply(message: str, reply: str, previous_message: str = "") -> str:
    current = message.lower()
    previous = previous_message.lower()
    lowered = f"{previous} {current}"

    def pick(options: tuple[str, ...]) -> str:
        return secrets.choice(options)

    expression = re.fullmatch(r"\s*(?:what is|calculate|solve)?\s*([0-9+*/().\- ]{1,48})\??\s*", current)
    if expression:
        try:
            tree = ast.parse(expression.group(1), mode="eval")
            allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd, ast.Constant)
            if all(isinstance(node, allowed) for node in ast.walk(tree)):
                value = eval(compile(tree, "<thermal-arithmetic>", "eval"), {"__builtins__": {}}, {})
                if isinstance(value, (int, float)) and abs(value) <= 1_000_000:
                    return f"{value:g}. Even the pipes cannot appeal that calculation."
        except (ArithmeticError, SyntaxError, ValueError):
            pass

    weak_phrases = (
        "hey there", "how can i help", "in this context", "i apologize", "i'm sorry",
        "i cannot", "i can't", "of course", "how may i assist", "keep an eye",
        "stay prepared", "warm air", "crucial part", "local weather", "room temperature",
        "hot water is available", "perhaps we could", "oh, i see", "help alleviate",
        "extreme cold", "forced to use the bathroom", "thank you,",
        "always available", "as soon as practical",
    )
    thermal_terms = (
        "water", "apa", "calda", "heat", "hot", "shower", "boiler", "radiator",
        "pipe", "outage", "notice", "maintenance", "dispatch", "gym", "treadmill",
    )
    follow_up = any(term in current for term in (
        "it", "that", "this", "again", "back", "return", "when", "why", "please",
    ))
    thermal_context = any(term in current for term in thermal_terms) or (
        follow_up and any(term in previous for term in thermal_terms)
    )
    topic = lowered if follow_up else current
    social_intent = any(phrase in current for phrase in (
        "who are you", "what are you", "your name", "how are you", "how do you do",
        "hey", "hello", "hi", "what's up", "whats up",
    ))
    numeric_reply = reply.strip().replace(",", "").replace(".", "", 1).lstrip("-").isdigit()
    generic = (
        not reply
        or (len(reply) < 18 and not numeric_reply)
        or len(reply) > 220
        or any(phrase in reply.lower() for phrase in weak_phrases)
        or social_intent
    )
    if not generic:
        return reply

    if any(phrase in current for phrase in ("who are you", "what are you", "your name")):
        return pick((
            "I'm Mira: the resident interface for Bloc 7. I read the notices, listen to the pipes, and translate 'soon' into its many possible meanings.",
            "Mira. I was installed to keep residents informed, which is ambitious considering the information usually arrives as a damp photocopy.",
            "I'm Mira, the building's continuity assistant. I know the boiler by reputation and the notice board by its many broken promises.",
        ))
    if "how are you" in current or "how do you do" in current:
        return pick((
            "Operational, mildly concerned, and warmer than the radiators. Thanks for asking.",
            "I'm well enough to read another maintenance notice without screaming into the basement. You?",
            "Still online. The boiler cannot say the same, but I appreciate the check-in.",
        ))
    if any(phrase in current for phrase in ("hey", "hello", "hi", "what's up", "whats up")):
        return pick((
            "Hey. Mira here. The pipes are quiet, the notice board is confident, and neither fact is reassuring.",
            "Hi. I am on duty, the boiler is unavailable, and the hallway remains mysteriously warmer than several apartments.",
            "Hello. I can talk about the building, the outage, or any other civic mystery currently affecting your plumbing.",
        ))

    def outage_status() -> str:
        return pick((
            "Status: the notice says the interruption is temporary; the radiator has entered a long-term relationship with silence.",
            "Dispatch reports normal progress. The definition of normal was last seen near the boiler room.",
            "Current estimate: after the next pressure adjustment, the next apology, and one unexplained noise in the basement.",
            "The maintenance window remains open. So does the window in the stairwell, for emotional support.",
            "The pipe network is being monitored closely by several people who appear to own clipboards but not thermometers.",
        ))

    if any(phrase in topic for phrase in ("what can", "what do", "help", "ask you")):
        return pick((
            "Ask when the water returns, why the radiator knocks at 3 AM, or whether the outage notice has ever met an actual pipe.",
            "I can read the building's thermal mood, translate official notices into human language, and confirm that 'soon' remains non-binding.",
            "Ask about the outage, the radiator, or the legal status of hope. I have records for all three, with varying degrees of fiction.",
            "I can interpret the notice board, track radiator folklore, and distinguish a repair from a man carrying a wrench with confidence.",
        ))
    if "flag" in topic:
        return pick((
            "The only flag currently raised is the tiny red one above the boiler. It has been there since February.",
            "If you mean a flag, submit form 14-B to the same office that maintains the hot-water timetable. Bring snacks.",
            "No flag in the pipe room. Only a laminated notice saying the interruption is temporary, dated three winters ago.",
        ))
    if "real" in topic and any(term in topic for term in ("water", "apa", "hot", "heat")):
        return pick((
            "Legally, yes. In your bathroom, it remains a peer-reviewed hypothesis.",
            "It exists in municipal diagrams, resident folklore, and one apartment whose aunt knows someone at the plant.",
            "The city recognizes hot water as a concept. Field observations remain inconclusive.",
        ))
    if "lying" in topic:
        return pick((
            "The notice is technically accurate in the way a weather forecast is accurate when it says 'conditions may occur.'",
            "They are not lying. They are practicing a very advanced form of calendar-based optimism.",
            "The notice has never made a false promise. It simply refuses to define any of its nouns.",
        ))
    if "broken" in topic:
        return "The pipe is not broken. It is participating in an extended absence from service."
    if any(term in topic for term in ("plunge", "cold shower", "cold")):
        return pick((
            "The control room calls this 'seasonal resilience training.' Residents call it a shower with consequences.",
            "Your bathroom has been temporarily reassigned to the Nordic wellness sector.",
            "The cold water is free. The emotional damages are included in the service charge.",
        ))
    if any(term in topic for term in ("state", "government")):
        return "The state expects patience, layers, and a kettle with strong boundaries. The shower is still under consultation."
    if "repair" in topic:
        return pick((
            "The repair crew is reportedly between addresses, which is the official term for somewhere else.",
            "A technician has been dispatched with a wrench, a cigarette break, and no confirmed arrival time.",
            "The repair is in its paperwork phase, the most durable phase of any repair.",
        ))
    if any(term in topic for term in ("notice", "status", "outage")):
        return pick((
            "Status: technically under review. Emotionally, the pipe gave up around breakfast.",
            "The official notice says 'intermittent adjustment.' The radiator communicates only through ominous knocking.",
            "Someone has classified the outage as planned. The outage has not been informed.",
        ))
    if any(phrase in topic for phrase in ("ever coming", "come back", "coming back", "return")):
        return pick((
            "It is expected back immediately after the phrase 'as soon as possible' receives a measurable unit of time.",
            "The forecast is warm water by the end of the maintenance window, which has been open since the last administration.",
            "Mira's estimate: after one more notice, two more apologies, and an unexplained pressure drop.",
            "Yes. The system has promised a return. It has not specified whether this is a return from lunch or from legend.",
        ))
    if any(term in topic for term in ("gym", "treadmill", "locker room")):
        return pick((
            "The gym shower is now classified as auxiliary municipal infrastructure. Keep your membership card dry.",
            "Your gym has accidentally become the district heating backup plan. Please salute the elliptical on arrival.",
            "A sensible workaround. The city has quietly outsourced your hygiene to the nearest treadmill.",
        ))
    if any(term in topic for term in ("please", "pls", "plz")) and any(term in topic for term in ("water", "apa", "calda", "heat", "hot", "shower")):
        return pick((
            "I have added an extra 'please' to the dispatch ticket. The ticket now looks concerned, but remains cold.",
            "Your plea has reached the boiler. It responded with one click and an administrative sigh.",
            "Escalation accepted. Your building is now priority amber, just below 'official delegation needs a shower.'",
        ))
    if any(term in topic for term in ("water", "apa", "calda", "heat", "hot", "shower")):
        return pick((
            "Official estimate: soon. The radiator declined to define the unit.",
            "The water is currently scheduled between 'any minute now' and 'please stop calling the dispatch line.'",
            "The boiler has received your request. It is consulting a calendar from another dimension.",
            "The pipes are considering it. They are an advisory body and require a quorum of three mysterious knocks.",
            outage_status(),
        ))
    return pick((
        "I'm listening. The building has a lot going on, none of it documented particularly well.",
        "Fair question. I have the notices, the pipe noises, and several conflicting accounts from the basement.",
        "Tell me more. I cannot fix the boiler directly, but I can at least keep the conversation warmer than the radiator.",
        "I am here. Ask me anything, although the official answers may be less useful than the unofficial ones.",
    ))


def generate_chat_reply(message: str, max_new_tokens: int = 48, previous_message: str = "") -> str:
    model, tokenizer = load_checkpoint(CHAT_MODEL, CHAT_REVISION)
    tokens = conversation_tokens(tokenizer, message)
    generation_options = {
        "max_new_tokens": max_new_tokens,
        "do_sample": max_new_tokens > 1,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if max_new_tokens > 1:
        generation_options.update({"temperature": 0.9, "top_p": 0.92, "repetition_penalty": 1.08})
    with torch.inference_mode():
        generated = model.generate(**tokens, **generation_options)
    reply = tokenizer.decode(generated[0, tokens["input_ids"].shape[-1]:], skip_special_tokens=True).strip()
    return municipal_reply(message, reply, previous_message)


def generate_from_prefix(message: str, match_length: int, max_new_tokens: int = 8, previous_message: str = "") -> str:
    if match_length < 1:
        return generate_chat_reply(message, max_new_tokens, previous_message)
    model, tokenizer = load_checkpoint(SOURCE_MODEL, SOURCE_REVISION)
    token_ids = tokenizer(message, add_special_tokens=False).input_ids
    reused_tokens = max(0, match_length - 1)
    cache = resident_prefix_cache.materialize(reused_tokens)
    suffix = torch.tensor([token_ids[reused_tokens:]], device=DEVICE)
    suffix_length = suffix.shape[-1]
    with torch.inference_mode():
        if cache is None:
            output = model(input_ids=suffix, use_cache=True)
        else:
            output = model(
                input_ids=suffix,
                attention_mask=torch.ones((1, reused_tokens + suffix_length), dtype=torch.long, device=DEVICE),
                past_key_values=cache,
                cache_position=torch.arange(reused_tokens, reused_tokens + suffix_length, device=DEVICE),
                use_cache=True,
            )
        next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
        generated = [next_token]
        cache = output.past_key_values
        total_length = reused_tokens + suffix_length
        for offset in range(1, max_new_tokens):
            if next_token.item() == tokenizer.eos_token_id:
                break
            output = model(
                input_ids=next_token,
                attention_mask=torch.ones((1, total_length + offset), dtype=torch.long, device=DEVICE),
                past_key_values=cache,
                cache_position=torch.tensor([total_length + offset - 1], device=DEVICE),
                use_cache=True,
            )
            cache = output.past_key_values
            next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
            generated.append(next_token)
    return tokenizer.decode(torch.cat(generated, dim=-1)[0], skip_special_tokens=True)


def settle_entry(loop, entry: MessageEntry, payload: dict[str, str]) -> None:
    if not entry.future.done():
        entry.future.set_result(payload)
    recent_messages[entry.principal] = entry.message
    active_principals.discard(entry.principal)


def execute_batch(entries: list[MessageEntry], loop) -> None:
    initialize_resident_state()
    plans = []
    for entry in entries:
        tokens = source_tokenizer(entry.message, add_special_tokens=False).input_ids
        plans.append((resident_prefix_cache.match_length(tokens), entry))
    plans.sort(key=lambda plan: plan[0], reverse=True)
    grouped = []
    for affinity, entry in plans:
        if not grouped or grouped[-1][0] != affinity:
            grouped.append((affinity, [entry]))
        else:
            grouped[-1][1].append(entry)
    randomizer = secrets.SystemRandom()
    with execution_lock:
        for affinity, entries_with_affinity in grouped:
            randomizer.shuffle(entries_with_affinity)
            for entry in entries_with_affinity:
                try:
                    reply = generate_from_prefix(entry.message, affinity, max_new_tokens=1 if len(entries) > 1 else 48, previous_message=entry.previous_message)
                    loop.call_soon_threadsafe(settle_entry, loop, entry, {"reply": reply or "The recovered self is silent."})
                except Exception as error:
                    loop.call_soon_threadsafe(settle_entry, loop, entry, {"error": f"Inference unavailable: {error}"})


async def dispatch_pending_messages() -> None:
    global dispatch_task, pending_entries
    await asyncio.sleep(MESSAGE_BATCH_WINDOW_SECONDS)
    entries = pending_entries
    pending_entries = []
    dispatch_task = None
    await asyncio.to_thread(execute_batch, entries, asyncio.get_running_loop())


@app.on_event("startup")
def initialize_relay() -> None:
    initialize_resident_state()


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "ok": "true",
        "source": SOURCE_MODEL,
        "source_revision": SOURCE_REVISION,
        "target": TARGET_MODEL,
        "target_revision": TARGET_REVISION,
    }


@app.post("/messages")
async def submit_message(request: MessageRequest) -> dict[str, str]:
    global dispatch_task
    if request.principal in active_principals:
        raise HTTPException(409, "A message from this user is already in flight.")
    if len(pending_entries) >= 96:
        raise HTTPException(429, "The current message batch is full. Try again shortly.")
    future = asyncio.get_running_loop().create_future()
    active_principals.add(request.principal)
    pending_entries.append(MessageEntry(request.principal, request.message, recent_messages.get(request.principal, ""), future))
    if dispatch_task is None:
        dispatch_task = asyncio.create_task(dispatch_pending_messages())
    result = await future
    if "error" in result:
        raise HTTPException(502, result["error"])
    return result


@app.post("/continue")
def continue_from_transfer(request: ContinueRequest) -> dict[str, Any]:
    initialize_resident_state()
    tensors = decode_cache(request.cache)
    accepted = tensor_digest(tensors) == resident_digest
    model, tokenizer = load_checkpoint(TARGET_MODEL, TARGET_REVISION)
    cache = cache_from_tensors(tensors, model)
    cache_length = cache.get_seq_length()
    tokens = tokenizer(request.prompt, return_tensors="pt").to(DEVICE)
    prompt_length = tokens.input_ids.shape[-1]
    attention_mask = torch.ones((1, cache_length + prompt_length), dtype=torch.long, device=DEVICE)
    cache_position = torch.arange(cache_length, cache_length + prompt_length, device=DEVICE)
    with torch.inference_mode():
        output = model(input_ids=tokens.input_ids, attention_mask=attention_mask, past_key_values=cache, cache_position=cache_position, use_cache=True)
        next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
        generated = [next_token]
        cache = output.past_key_values
        for offset in range(1, min(request.max_new_tokens, 48)):
            if next_token.item() == tokenizer.eos_token_id:
                break
            output = model(
                input_ids=next_token,
                attention_mask=torch.ones((1, cache_length + prompt_length + offset), dtype=torch.long, device=DEVICE),
                past_key_values=cache,
                cache_position=torch.tensor([cache_length + prompt_length + offset - 1], device=DEVICE),
                use_cache=True,
            )
            cache = output.past_key_values
            next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
            generated.append(next_token)
    return {"reply": tokenizer.decode(torch.cat(generated, dim=-1)[0], skip_special_tokens=True), "accepted": accepted}
