#!/usr/bin/env python3
"""Verify supplied cache integrity, layout and integer classifier arithmetic.

This is an offline data verifier, not a challenge solver or acceptance oracle.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "challenge/give_to_player/local-data"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(meta, raw, manifest):
    require(meta["schema"] == "residuegate-qwen-cache-v1", "unsupported schema")
    hashes = {}
    for name, data, key in (
        ("qwen_cache.bin", raw, "binary_sha256"),
        ("manifest.txt", manifest, "manifest_sha256"),
    ):
        hashes[name] = hashlib.sha256(data).hexdigest()
        require(hashes[name] == meta[key], f"{name}: SHA-256 mismatch")
    require(raw[:8] == b"RGQWEN1\0", "invalid magic")
    count, variants, dim = (meta[k] for k in
                            ("count", "variant_count", "embedding_dimension"))
    require(all(type(x) is int and x > 0 for x in (count, variants, dim)),
            "invalid dimensions")
    record_size = 32 + dim
    entry_size = 32 + variants * record_size
    require(meta["entry_size"] == entry_size, "inconsistent entry size")
    require(len(raw) == 8 + count * entry_size, "invalid file size")
    weight, bias = meta["head_weight"], meta["head_bias"]
    require(len(weight) == len(bias) and len(bias) >= 2, "invalid head shape")
    require(all(len(row) == dim for row in weight), "invalid weight dimensions")
    require(all(type(x) is int for row in weight for x in row)
            and all(type(x) is int for x in bias), "noninteger classifier")
    rows = []
    for entry in range(count):
        for variant in range(variants):
            start = 8 + entry * entry_size + 32 + variant * record_size + 32
            embedding = [x if x < 128 else x - 256 for x in raw[start:start + dim]]
            logits = [b + sum(w * e for w, e in zip(row, embedding))
                      for row, b in zip(weight, bias)]
            order = sorted(range(len(logits)), key=lambda c: (-logits[c], c))
            rows.append({"entry": entry, "variant": variant,
                         "embedding": embedding, "logits": logits,
                         "top": order[0],
                         "margin": logits[order[0]] - logits[order[1]]})
    return {"scope": "cache integrity, structural consistency, integer arithmetic",
            "integrity_and_layout": "passed", "sha256": hashes,
            "record_count": len(rows), "rows": rows,
            "vision_pipeline_verified": False,
            "challenge_acceptance_verified": False,
            "challenge_status": "unsolved"}


if __name__ == "__main__":
    metadata = json.loads((DATA / "qwen_cache.json").read_text())
    report = verify(metadata, (DATA / "qwen_cache.bin").read_bytes(),
                    (DATA / "manifest.txt").read_bytes())
    print(json.dumps(report, indent=2))
