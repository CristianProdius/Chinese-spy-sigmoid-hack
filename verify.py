#!/usr/bin/env python3
"""Self-check for main.py without the real data.

For each case, encode a bilingual calibration text and a challenge message (with a
SIGMOID_TEST flag) the way a puzzle author would, write test-input.json into its own
directory, run main.py there, and compare the result with the truth.

    uv run python verify.py               # run every case through main.py
    uv run python verify.py --collisions  # also scan every candidate for exact collisions
    uv run python verify.py --only cl100k_base,gpt2
Writes verify-report.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

import main as solver

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("VERIFY_DIR", "/tmp/nlp-us-verify")

CALIBRATION = (
    "Welcome to the Great American Token Lab! Bienvenidos al laboratorio de idiomas.\n"
    "¿Dónde está la biblioteca? It's on Main Street, next to the café; ¡qué bonito!\n"
    "Mañana mis niños y yo vamos a San Antonio 🇺🇸🌮, and we'll grab tacos al pastor for $12.50.\n"
    "\"Good morning,\" said Ms. Peña to señor Núñez. 100% bilingual, 24/7, from Texas to Nueva York."
)
CHALLENGE = (
    "Mensaje confidencial: la piñata está escondida en el jardín, junto al árbol.\n"
    "The secret flag is SIGMOID_TEST and nobody else should know it. ¿Entendido? ¡Sí, claro! 🎉"
)
# p50k_base only differs from gpt2/r50k_base on runs of spaces, so its challenge has some.
CHALLENGE_SPACES = CHALLENGE + "\n    def flag():\n        return 'SIGMOID_TEST'"


def tiktoken_encoder(name):
    import tiktoken
    enc = tiktoken.get_encoding(name)
    return lambda text: enc.encode(text)


def hf_encoder(repo):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo, local_files_only=True)
    return lambda text: tok.encode(text)


def hf_encoder_plain(repo, suffix=()):
    """encode(add_special_tokens=False), optionally with special ids appended by hand."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo, local_files_only=solver.repo_is_cached(repo))
    return lambda text: tok.encode(text, add_special_tokens=False) + list(suffix)


def tokenizers_encoder(repo):
    from tokenizers import Tokenizer
    tk = Tokenizer.from_file(solver.cached_file(repo, "tokenizer.json"))
    return lambda text: tk.encode(text).ids


def spm_encoder(repo, filename):
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(model_file=solver.cached_file(repo, filename))
    return lambda text: list(sp.encode(text))


# (case name, expected tokenizer id, how the author encodes, challenge text)
CASES = [
    ("cl100k_base", "cl100k_base", lambda: tiktoken_encoder("cl100k_base"), CHALLENGE),
    ("o200k_base", "o200k_base", lambda: tiktoken_encoder("o200k_base"), CHALLENGE),
    ("p50k_base+spaces", "p50k_base", lambda: tiktoken_encoder("p50k_base"), CHALLENGE_SPACES),
    ("gpt2 (transformers)", "gpt2", lambda: hf_encoder("openai-community/gpt2"), CHALLENGE),
    ("bert-base-uncased", "bert-base-uncased", lambda: hf_encoder("google-bert/bert-base-uncased"), CHALLENGE),
    ("bert-base-multilingual-cased", "bert-base-multilingual-cased",
     lambda: hf_encoder("google-bert/bert-base-multilingual-cased"), CHALLENGE),
    ("xlm-roberta-base", "xlm-roberta-base", lambda: hf_encoder("FacebookAI/xlm-roberta-base"), CHALLENGE),
    ("xlm-roberta raw sentencepiece", "xlm-roberta-base",
     lambda: spm_encoder("FacebookAI/xlm-roberta-base", "sentencepiece.bpe.model"), CHALLENGE),
    ("t5-base", "t5-base", lambda: hf_encoder("google-t5/t5-base"), CHALLENGE),
    ("mt5 raw sentencepiece", "google/mt5-small", lambda: spm_encoder("google/mt5-small", "spiece.model"), CHALLENGE),
    ("Llama-2", "meta-llama/Llama-2-7b-hf", lambda: hf_encoder("NousResearch/Llama-2-7b-hf"), CHALLENGE),
    ("Llama-2 raw sentencepiece", "meta-llama/Llama-2-7b-hf",
     lambda: spm_encoder("NousResearch/Llama-2-7b-hf", "tokenizer.model"), CHALLENGE),
    ("Llama-3", "meta-llama/Meta-Llama-3-8B", lambda: hf_encoder("NousResearch/Meta-Llama-3-8B"), CHALLENGE),
    ("Mistral-7B-v0.1", "mistralai/Mistral-7B-v0.1", lambda: hf_encoder("mistralai/Mistral-7B-v0.1"), CHALLENGE),
    ("Qwen2.5", "Qwen/Qwen2.5-0.5B", lambda: hf_encoder("Qwen/Qwen2.5-0.5B"), CHALLENGE),
    ("gemma-2b", "google/gemma-2b", lambda: hf_encoder("unsloth/gemma-2b"), CHALLENGE),
    ("bloom (tokenizers lib)", "bigscience/bloom-560m",
     lambda: tokenizers_encoder("bigscience/bloom-560m"), CHALLENGE),
    ("gpt-neox-20b", "EleutherAI/gpt-neox-20b", lambda: hf_encoder("EleutherAI/gpt-neox-20b"), CHALLENGE),
    ("BETO cased", "dccuchile/bert-base-spanish-wwm-cased",
     lambda: hf_encoder("dccuchile/bert-base-spanish-wwm-cased"), CHALLENGE),
    ("opus-mt-en-es", "Helsinki-NLP/opus-mt-en-es", lambda: hf_encoder("Helsinki-NLP/opus-mt-en-es"), CHALLENGE),
    ("nllb-200", "facebook/nllb-200-distilled-600M",
     lambda: hf_encoder("facebook/nllb-200-distilled-600M"), CHALLENGE),
    ("byt5", "google/byt5-small", lambda: hf_encoder("google/byt5-small"), CHALLENGE),
    ("deberta-v3", "microsoft/deberta-v3-base", lambda: hf_encoder("microsoft/deberta-v3-base"), CHALLENGE),
    ("Phi-3-mini", "microsoft/Phi-3-mini-4k-instruct",
     lambda: hf_encoder("microsoft/Phi-3-mini-4k-instruct"), CHALLENGE),
    ("bart-base (shares roberta vocab)", "facebook/bart-base", lambda: hf_encoder("facebook/bart-base"), CHALLENGE),
    ("o200k_harmony (shares o200k)", "o200k_harmony", lambda: tiktoken_encoder("o200k_harmony"), CHALLENGE),
    # --- edge cases ---
    ("edge: gpt2 + <|endoftext|> by hand", "gpt2",
     lambda: hf_encoder_plain("openai-community/gpt2", [50256]), CHALLENGE),
    ("edge: bert-base-cased no specials", "bert-base-cased",
     lambda: hf_encoder_plain("google-bert/bert-base-cased"), CHALLENGE),
    ("edge: Llama-2 no BOS", "meta-llama/Llama-2-7b-hf",
     lambda: hf_encoder_plain("NousResearch/Llama-2-7b-hf"), CHALLENGE),
    ("edge: Llama-3 no BOS", "meta-llama/Meta-Llama-3-8B",
     lambda: hf_encoder_plain("NousResearch/Meta-Llama-3-8B"), CHALLENGE),
    ("edge: scibert (not a candidate)", "allenai/scibert_scivocab_uncased",
     lambda: hf_encoder_plain("allenai/scibert_scivocab_uncased"), CHALLENGE),
]


def slug(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name).strip("_")


def build_cases(selected):
    built = []
    for name, expected, make, challenge in selected:
        encode = make()
        case_dir = os.path.join(WORK, slug(name))
        os.makedirs(case_dir, exist_ok=True)
        data = {"calibration": {"text": CALIBRATION, "token_ids": encode(CALIBRATION)},
                "challenge": {"token_ids": encode(challenge)}}
        with open(os.path.join(case_dir, "test-input.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        built.append({"name": name, "expected": expected, "dir": case_dir, "challenge": challenge,
                      "calib_ids": data["calibration"]["token_ids"]})
    return built


def collision_scan(cases):
    """Every candidate engine/variant that reproduces each case's calibration ids exactly."""
    solver.NET["ok"] = False
    hits = {c["name"]: [] for c in cases}
    for out_id, kind, sources, _ in solver.CANDIDATES:
        for engine in solver.engines_for(kind, sources):
            try:
                variants = [(lbl + tl, ids) for tl, t in solver.text_variants(CALIBRATION)
                            for lbl, ids in engine.encodings(t)]
            except Exception:
                continue
            for c in cases:
                for lbl, ids in variants:
                    if ids == c["calib_ids"]:
                        tag = out_id
                        if tag not in hits[c["name"]]:
                            hits[c["name"]].append(tag)
                        break
    return hits


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    selected = [c for c in CASES if not only or c[1] in only or c[0] in only]
    cases = build_cases(selected)
    collisions = collision_scan(cases) if "--collisions" in sys.argv else {}

    rows = []
    for c in cases:
        t0 = time.time()
        proc = subprocess.run([sys.executable, os.path.join(HERE, "main.py"), "--quiet"], cwd=c["dir"],
                              capture_output=True, text=True, timeout=900)
        took = time.time() - t0
        try:
            with open(os.path.join(c["dir"], "test-output.json"), encoding="utf-8") as fh:
                out = json.load(fh)
        except Exception:
            out = {"tokenizer_id": "", "decoded_message": ""}
        got_text = solver.normalise(out.get("decoded_message", ""))
        want_text = solver.normalise(c["challenge"])
        equivalent = collisions.get(c["name"], [])
        row = {
            "case": c["name"], "expected": c["expected"], "got": out.get("tokenizer_id"),
            "id_ok": out.get("tokenizer_id", "").lower() == c["expected"].lower(),
            "id_equivalent": out.get("tokenizer_id") in equivalent,
            "text_exact": got_text == want_text,
            "text_similarity": round(solver.text_similarity(got_text, want_text), 4),
            "seconds": round(took, 1),
            "exact_collisions": equivalent,
            "decoded": out.get("decoded_message"),
            "exit_code": proc.returncode,
        }
        rows.append(row)
        print(f"{row['case']:<34} expected={row['expected']:<34} got={row['got']:<34} "
              f"id={'OK' if row['id_ok'] else ('EQUIV' if row['id_equivalent'] else 'FAIL')} "
              f"text={'EXACT' if row['text_exact'] else row['text_similarity']} {took:5.1f}s", flush=True)
        if not row["text_exact"]:
            print(f"    decoded: {row['decoded']!r}", flush=True)
        if equivalent and len(equivalent) > 1:
            print(f"    collisions: {', '.join(equivalent)}", flush=True)
    with open(os.path.join(HERE, "verify-report.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
