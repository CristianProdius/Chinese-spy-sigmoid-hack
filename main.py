#!/usr/bin/env python3
"""The Great American Token Mystery.

Find the subword tokenizer whose encoding of the calibration text equals the
calibration token IDs, then decode the challenge token IDs with it.

    uv run python main.py [input.json] [output.json] [--all] [--only id1,id2] [--quiet]

Defaults: reads ./test-input.json, writes ./test-output.json.
  --all    score every candidate instead of stopping at the first perfect match
           (slower; shows every tokenizer that collides with the winner)
  --only   restrict the search to these output ids (comma separated)
  --quiet  no per-candidate log lines on stderr
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import warnings
from collections import Counter
from difflib import SequenceMatcher

warnings.filterwarnings("ignore")  # e.g. Marian's "pip install sacremoses" hint

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TIKTOKEN_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".cache", "tiktoken"))

TT, HF = "tiktoken", "hf"

# (output id, kind, sources to load from in order, vocab-size hint or None).
# List order is the preference order: when several tokenizers reproduce the
# calibration IDs exactly, the earliest one wins. Inside every group of
# tokenizers that share a vocabulary, the canonical name comes first.
# The hint is the largest vocab over all engines of the candidate (from
# prefetch.py); a candidate is skipped when an input id is >= its hint.
CANDIDATES: list[tuple[str, str, list[str], int | None]] = [
    # --- OpenAI tiktoken encodings -------------------------------------------------
    ("cl100k_base", TT, ["cl100k_base"], 100277),
    ("o200k_base", TT, ["o200k_base"], 200019),
    ("gpt2", TT, ["gpt2"], 50257),
    ("r50k_base", TT, ["r50k_base"], 50257),            # same ranks as gpt2
    ("p50k_base", TT, ["p50k_base"], 50281),            # gpt2 + whitespace-run tokens
    ("p50k_edit", TT, ["p50k_edit"], 50284),            # p50k_base + FIM specials
    ("o200k_harmony", TT, ["o200k_harmony"], 201088),   # o200k_base + specials
    # --- Hugging Face: the classics -------------------------------------------------
    ("gpt2", HF, ["openai-community/gpt2"], 50257),
    ("bert-base-uncased", HF, ["google-bert/bert-base-uncased"], 30522),
    ("bert-base-cased", HF, ["google-bert/bert-base-cased"], 28996),
    ("bert-base-multilingual-cased", HF, ["google-bert/bert-base-multilingual-cased"], 119547),
    ("bert-base-multilingual-uncased", HF, ["google-bert/bert-base-multilingual-uncased"], 105879),
    ("roberta-base", HF, ["FacebookAI/roberta-base"], 50265),
    ("xlm-roberta-base", HF, ["FacebookAI/xlm-roberta-base"], 250002),
    ("t5-base", HF, ["google-t5/t5-base"], 32100),
    ("google/mt5-small", HF, ["google/mt5-small"], 250100),
    ("meta-llama/Llama-2-7b-hf", HF, ["NousResearch/Llama-2-7b-hf",
                                      "hf-internal-testing/llama-tokenizer"], 32000),
    ("meta-llama/Meta-Llama-3-8B", HF, ["NousResearch/Meta-Llama-3-8B",
                                        "NousResearch/Meta-Llama-3.1-8B-Instruct"], 128256),
    ("mistralai/Mistral-7B-v0.1", HF, ["mistralai/Mistral-7B-v0.1", "unsloth/mistral-7b",
                                       "HuggingFaceH4/zephyr-7b-beta"], 32000),
    ("Qwen/Qwen2.5-0.5B", HF, ["Qwen/Qwen2.5-0.5B"], 151665),
    ("google/gemma-2b", HF, ["unsloth/gemma-2b"], 256000),
    ("bigscience/bloom-560m", HF, ["bigscience/bloom-560m"], 250680),
    ("EleutherAI/gpt-neox-20b", HF, ["EleutherAI/gpt-neox-20b"], 50277),
    ("tiiuae/falcon-7b", HF, ["tiiuae/falcon-7b"], 65024),
    ("facebook/opt-125m", HF, ["facebook/opt-125m"], 50265),
    ("google/byt5-small", HF, ["google/byt5-small"], 384),
    ("albert-base-v2", HF, ["albert/albert-base-v2"], 30000),
    ("xlnet-base-cased", HF, ["xlnet/xlnet-base-cased"], 32000),
    ("microsoft/deberta-v3-base", HF, ["microsoft/deberta-v3-base"], 128001),
    ("microsoft/mdeberta-v3-base", HF, ["microsoft/mdeberta-v3-base"], 250102),
    ("camembert-base", HF, ["almanach/camembert-base"], 32006),
    # --- Spanish / bilingual / translation -------------------------------------------
    ("dccuchile/bert-base-spanish-wwm-cased", HF, ["dccuchile/bert-base-spanish-wwm-cased"], 31002),
    ("dccuchile/bert-base-spanish-wwm-uncased", HF, ["dccuchile/bert-base-spanish-wwm-uncased"], 31002),
    ("PlanTL-GOB-ES/roberta-base-bne", HF, ["JonatanGk/roberta-base-bne-finetuned-sqac"], 50262),
    ("PlanTL-GOB-ES/gpt2-base-bne", HF, ["joancipria/gpt2-base-bne-FineTunedEmoEvent"], 50264),
    ("bertin-project/bertin-roberta-base-spanish", HF, ["bertin-project/bertin-roberta-base-spanish"], 50262),
    ("DeepESP/gpt2-spanish", HF, ["DeepESP/gpt2-spanish"], 50257),
    ("Helsinki-NLP/opus-mt-en-es", HF, ["Helsinki-NLP/opus-mt-en-es"], 65001),
    ("Helsinki-NLP/opus-mt-es-en", HF, ["Helsinki-NLP/opus-mt-es-en"], 65001),
    ("facebook/nllb-200-distilled-600M", HF, ["facebook/nllb-200-distilled-600M"], 256204),
    ("facebook/m2m100_418M", HF, ["facebook/m2m100_418M"], 128104),
    ("facebook/mbart-large-50", HF, ["facebook/mbart-large-50"], 250054),
    ("facebook/mbart-large-cc25", HF, ["facebook/mbart-large-cc25"], 250027),
    ("facebook/xglm-564M", HF, ["facebook/xglm-564M"], 256008),
    ("sentence-transformers/LaBSE", HF, ["sentence-transformers/LaBSE"], 501153),
    ("openai/whisper-small", HF, ["openai/whisper-small"], 51865),
    ("google/umt5-small", HF, ["google/umt5-small"], 256300),
    ("google/rembert", HF, ["google/rembert"], 250300),
    ("ai-forever/mGPT", HF, ["ai-forever/mGPT"], 100000),
    ("BSC-LT/salamandra-2b", HF, ["BSC-LT/salamandra-2b"], 256000),
    # --- Newer LLM families ----------------------------------------------------------
    ("meta-llama/Llama-3.1-8B", HF, ["NousResearch/Meta-Llama-3.1-8B-Instruct"], 128256),
    ("mistralai/Mistral-7B-v0.3", HF, ["mistralai/Mistral-7B-v0.3", "unsloth/mistral-7b-v0.3"], 32768),
    ("mistralai/Mistral-Nemo-Instruct-2407", HF, ["mistralai/Mistral-Nemo-Instruct-2407"], 131072),
    ("Qwen/Qwen2-0.5B", HF, ["Qwen/Qwen2-0.5B"], 151646),
    ("Qwen/Qwen3-0.6B", HF, ["Qwen/Qwen3-0.6B", "Qwen/Qwen3-8B"], 151669),
    ("Qwen/Qwen3.5-2B", HF, ["Qwen/Qwen3.5-2B"], 248077),
    ("google/gemma-2-2b", HF, ["unsloth/gemma-2-2b"], 256000),
    ("google/gemma-3-4b-it", HF, ["unsloth/gemma-3-4b-it"], 262145),
    ("microsoft/phi-2", HF, ["microsoft/phi-2"], 50295),
    ("microsoft/Phi-3-mini-4k-instruct", HF, ["microsoft/Phi-3-mini-4k-instruct"], 32011),
    ("microsoft/phi-4", HF, ["microsoft/phi-4"], 100352),
    ("deepseek-ai/deepseek-llm-7b-base", HF, ["deepseek-ai/deepseek-llm-7b-base"], 100015),
    ("deepseek-ai/deepseek-coder-1.3b-base", HF, ["deepseek-ai/deepseek-coder-1.3b-base"], 32022),
    ("deepseek-ai/DeepSeek-V3", HF, ["deepseek-ai/DeepSeek-V3"], 128815),
    ("01-ai/Yi-6B", HF, ["01-ai/Yi-6B"], 64000),
    ("bigcode/starcoder", HF, ["bigcode/tiny_starcoder_py"], 49152),
    ("bigcode/starcoder2-3b", HF, ["bigcode/starcoder2-3b"], 49152),
    ("Salesforce/codegen-350M-mono", HF, ["Salesforce/codegen-350M-mono"], 50295),
    ("stabilityai/stablelm-2-1_6b", HF, ["stabilityai/stablelm-2-1_6b"], 100289),
    ("HuggingFaceTB/SmolLM2-135M", HF, ["HuggingFaceTB/SmolLM2-135M"], 49152),
    ("allenai/OLMo-2-0425-1B", HF, ["allenai/OLMo-2-0425-1B"], 100278),
    # --- Other encoders ---------------------------------------------------------------
    ("microsoft/deberta-base", HF, ["microsoft/deberta-base"], 50265),
    ("sentence-transformers/all-mpnet-base-v2", HF, ["sentence-transformers/all-mpnet-base-v2"], 30527),
    ("openai/clip-vit-base-patch32", HF, ["openai/clip-vit-base-patch32"], 49408),
    ("google/canine-s", HF, ["google/canine-s"], 1114112),
    ("google/pegasus-large", HF, ["google/pegasus-large"], 96103),
    ("google/bigbird-roberta-base", HF, ["google/bigbird-roberta-base"], 50358),
    # --- Same vocabulary as an earlier entry (never win a tie; kept for collision reports) ---
    ("distilgpt2", HF, ["distilbert/distilgpt2"], 50257),
    ("EleutherAI/gpt-neo-125m", HF, ["EleutherAI/gpt-neo-125m"], 50257),
    ("EleutherAI/gpt-j-6b", HF, ["EleutherAI/gpt-j-6b"], 50400),
    ("distilbert-base-uncased", HF, ["distilbert/distilbert-base-uncased"], 30522),
    ("google/electra-base-discriminator", HF, ["google/electra-base-discriminator"], 30522),
    ("sentence-transformers/all-MiniLM-L6-v2", HF, ["sentence-transformers/all-MiniLM-L6-v2"], 30522),
    ("distilbert-base-cased", HF, ["distilbert/distilbert-base-cased"], 28996),
    ("distilbert-base-multilingual-cased", HF, ["distilbert/distilbert-base-multilingual-cased"], 119547),
    ("sentence-transformers/distiluse-base-multilingual-cased-v2",
     HF, ["sentence-transformers/distiluse-base-multilingual-cased-v2"], 119547),
    ("distilroberta-base", HF, ["distilbert/distilroberta-base"], 50265),
    ("facebook/bart-base", HF, ["facebook/bart-base"], 50265),
    ("allenai/longformer-base-4096", HF, ["allenai/longformer-base-4096"], 50265),
    ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
     HF, ["sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"], 250002),
    ("intfloat/multilingual-e5-base", HF, ["intfloat/multilingual-e5-base"], 250002),
    ("BAAI/bge-m3", HF, ["BAAI/bge-m3"], 250002),
    ("t5-small", HF, ["google-t5/t5-small"], 32100),
    ("google/flan-t5-base", HF, ["google/flan-t5-base"], 32100),
    ("EleutherAI/pythia-160m", HF, ["EleutherAI/pythia-160m"], 50277),
    ("huggyllama/llama-7b", HF, ["huggyllama/llama-7b"], 32000),
    ("TinyLlama/TinyLlama-1.1B-Chat-v1.0", HF, ["TinyLlama/TinyLlama-1.1B-Chat-v1.0"], 32000),
]

# Files a tokenizer may need. Never weights.
TOKENIZER_FILES = [
    "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "added_tokens.json",
    "vocab.json", "vocab.txt", "merges.txt", "config.json", "normalizer.json",
    "chat_template.jinja", "chat_template.json",
    "tokenizer.model", "spiece.model", "sentencepiece.bpe.model", "sentencepiece.model", "spm.model",
    "source.spm", "target.spm",
]
SPM_FILES = ["tokenizer.model", "spiece.model", "sentencepiece.bpe.model", "sentencepiece.model",
             "spm.model", "source.spm"]

FLAG_RE = re.compile(r"sigmoid\s*_\s*[a-z0-9]+", re.I)
_OFFLINE_VALUES = {"1", "true", "yes", "on"}
NET = {"ok": os.environ.get("HF_HUB_OFFLINE", "").lower() not in _OFFLINE_VALUES}
QUIET = False


def log(*args) -> None:
    if not QUIET:
        print(*args, file=sys.stderr, flush=True)


def is_network_error(exc: BaseException) -> bool:
    text = f"{type(exc).__name__} {exc}".lower()
    return any(s in text for s in ("connect", "timeout", "timed out", "offline", "name resolution",
                                   "temporary failure", "network is unreachable"))


# ---------------------------------------------------------------------------- engines

class Engine:
    """One concrete way to run a tokenizer (tiktoken, transformers, tokenizers, raw sentencepiece)."""

    label = "?"
    vocab_size = 0
    special_ids: set[int] = set()
    wrap_ids: set[int] = set()  # BOS/EOS/CLS/SEP ids someone may have added by hand

    def encodings(self, text: str) -> list[tuple[str, list[int]]]:
        raise NotImplementedError

    def decode(self, ids: list[int]) -> str:
        """Decode, dropping special tokens."""
        raise NotImplementedError

    def decode_raw(self, ids: list[int]) -> str:
        """Decode, keeping special tokens (debug only)."""
        return self.decode(ids)

    def valid(self, ids: list[int]) -> list[int]:
        return [i for i in ids if 0 <= i < self.vocab_size]


class TiktokenEngine(Engine):
    def __init__(self, name: str):
        import tiktoken
        self.enc = tiktoken.get_encoding(name)
        self.label = f"tiktoken:{name}"
        self.vocab_size = self.enc.n_vocab
        special = getattr(self.enc, "_special_tokens", None)
        if special is None:
            special = {s: self.enc.encode_single_token(s) for s in self.enc.special_tokens_set}
        self.special_ids = set(special.values())
        self.wrap_ids = {self.enc.eot_token} if getattr(self.enc, "eot_token", None) is not None else set()

    def encodings(self, text):
        return [("encode_ordinary", self.enc.encode_ordinary(text)),
                ("encode(allowed_special=all)", self.enc.encode(text, allowed_special="all"))]

    def _decodable(self, ids):
        known = []
        for i in ids:
            try:
                self.enc.decode_single_token_bytes(i)
                known.append(i)
            except Exception:
                pass
        return known

    def decode(self, ids):
        return self.enc.decode([i for i in self._decodable(ids) if i not in self.special_ids], errors="replace")

    def decode_raw(self, ids):
        return self.enc.decode(self._decodable(ids), errors="replace")


class HFEngine(Engine):
    def __init__(self, tok, repo: str):
        self.tok = tok
        self.label = f"transformers:{repo}"
        self.vocab_size = len(tok)
        special = set(getattr(tok, "all_special_ids", []) or [])
        for i, t in (getattr(tok, "added_tokens_decoder", {}) or {}).items():
            if getattr(t, "special", False):
                special.add(int(i))
        self.special_ids = {i for i in special if i is not None}
        self.wrap_ids = {i for i in (tok.bos_token_id, tok.eos_token_id, tok.cls_token_id, tok.sep_token_id)
                         if i is not None}

    def encodings(self, text):
        return [("encode(add_special_tokens=True)", list(self.tok.encode(text, add_special_tokens=True))),
                ("encode(add_special_tokens=False)", list(self.tok.encode(text, add_special_tokens=False)))]

    def decode(self, ids):
        return self.tok.decode(self.valid(ids), skip_special_tokens=True)

    def decode_raw(self, ids):
        return self.tok.decode(self.valid(ids), skip_special_tokens=False)


class TokenizersEngine(Engine):
    def __init__(self, path: str, repo: str):
        from tokenizers import Tokenizer
        self.tk = Tokenizer.from_file(path)
        self.label = f"tokenizers:{repo}/tokenizer.json"
        self.vocab_size = self.tk.get_vocab_size(with_added_tokens=True)
        self.special_ids = {int(i) for i, t in self.tk.get_added_tokens_decoder().items() if t.special}

    def encodings(self, text):
        return [("Tokenizer.encode(add_special_tokens=True)", self.tk.encode(text, add_special_tokens=True).ids),
                ("Tokenizer.encode(add_special_tokens=False)", self.tk.encode(text, add_special_tokens=False).ids)]

    def decode(self, ids):
        return self.tk.decode(self.valid(ids), skip_special_tokens=True)

    def decode_raw(self, ids):
        return self.tk.decode(self.valid(ids), skip_special_tokens=False)


class SPMEngine(Engine):
    def __init__(self, path: str, repo: str, filename: str):
        import sentencepiece as spm
        self.sp = spm.SentencePieceProcessor(model_file=path)
        self.label = f"sentencepiece:{repo}/{filename}"
        self.vocab_size = self.sp.get_piece_size()
        self.bos, self.eos = self.sp.bos_id(), self.sp.eos_id()
        self.special_ids = {i for i in (self.bos, self.eos, self.sp.pad_id()) if i >= 0}
        self.wrap_ids = {i for i in (self.bos, self.eos) if i >= 0}

    def encodings(self, text):
        return [("sp.encode", list(self.sp.encode(text)))]

    def decode(self, ids):
        return self.sp.decode([i for i in self.valid(ids) if i not in self.special_ids])

    def decode_raw(self, ids):
        return "".join(self.sp.id_to_piece(i) for i in self.valid(ids))


# ---------------------------------------------------------------------------- loading

def cached_file(repo: str, filename: str) -> str | None:
    from huggingface_hub import try_to_load_from_cache
    try:
        path = try_to_load_from_cache(repo, filename)
    except Exception:
        return None
    return path if isinstance(path, str) and os.path.exists(path) else None


def repo_is_cached(repo: str) -> bool:
    return any(cached_file(repo, f) for f in ("tokenizer.json", "tokenizer_config.json", "vocab.txt",
                                              "vocab.json", *SPM_FILES))


def ensure_repo(repo: str) -> bool:
    """Make sure the repo's tokenizer files are in the HF cache. Downloads only when online."""
    if repo_is_cached(repo):
        return True
    if not NET["ok"]:
        return False
    from huggingface_hub import snapshot_download
    try:
        snapshot_download(repo, allow_patterns=TOKENIZER_FILES)
    except Exception as exc:  # gated, missing, or no network
        if is_network_error(exc):
            NET["ok"] = False
            log(f"  network unavailable, staying offline ({type(exc).__name__})")
        else:
            log(f"  {repo}: download failed: {type(exc).__name__}: {str(exc).splitlines()[0][:120]}")
        return False
    return repo_is_cached(repo)


def engine_factories(kind: str, sources: list[str]):
    """Yield (engine type, factory) for a candidate, cheapest and most likely first.
    Factories are lazy so the caller can skip loading engines it doesn't need."""
    if kind == TT:
        yield "tiktoken", lambda: TiktokenEngine(sources[0])
        return
    for repo in sources:
        if not ensure_repo(repo):
            continue

        def hf(repo=repo):
            from transformers import AutoTokenizer
            return HFEngine(AutoTokenizer.from_pretrained(repo, local_files_only=True, trust_remote_code=False), repo)

        yield "transformers", hf
        path = cached_file(repo, "tokenizer.json")
        if path:
            yield "tokenizers", lambda path=path, repo=repo: TokenizersEngine(path, repo)
        for fn in SPM_FILES:
            path = cached_file(repo, fn)
            if path:
                yield "sentencepiece", lambda path=path, repo=repo, fn=fn: SPMEngine(path, repo, fn)
        return  # the first source that is available is the one we use


def engines_for(kind: str, sources: list[str]):
    """Load every engine of a candidate (used by prefetch.py and verify.py)."""
    for etype, make in engine_factories(kind, sources):
        try:
            yield make()
        except Exception as exc:
            if etype != "sentencepiece":  # a tiktoken-format tokenizer.model is expected to fail
                log(f"  {etype} failed for {sources}: {type(exc).__name__}: {str(exc).splitlines()[0][:120] if str(exc) else ''}")


# ---------------------------------------------------------------------------- scoring

def strip_special(ids: list[int], special: set[int]) -> list[int]:
    lo, hi = 0, len(ids)
    while lo < hi and ids[lo] in special:
        lo += 1
    while hi > lo and ids[hi - 1] in special:
        hi -= 1
    return ids[lo:hi]


def id_similarity(a: list[int], b: list[int]) -> float:
    if not a or not b:
        return 0.0
    n = max(len(a), len(b))
    lcp = 0
    for x, y in zip(a, b):
        if x != y:
            break
        lcp += 1
    overlap = sum((Counter(a) & Counter(b)).values()) / n
    return 0.5 * overlap + 0.5 * lcp / n


def text_variants(text: str) -> list[tuple[str, str]]:
    out = [("", text)]
    if text.strip() != text:
        out.append((" on text.strip()", text.strip()))
    out.append((" on ' '+text", " " + text))
    return out


def match(engine: Engine, text: str, target: list[int]) -> tuple[int, float, str]:
    """Match levels:
    3 = the engine's own encode() output equals the ids exactly
    2 = same ids once a single BOS/EOS/CLS/SEP token is added by hand at either end
    1 = same ids between the special tokens, other special tokens around them
    0 = no match; the float is a fuzzy similarity used only as a fallback
    """
    best = (0, 0.0, "")
    core_target = strip_special(target, engine.special_ids)
    for tlabel, t in text_variants(text):
        for elabel, ids in engine.encodings(t):
            if ids == target:
                return 3, 1.0, elabel + tlabel
            core = strip_special(ids, engine.special_ids)
            if core_target and core == core_target:
                start = target.index(core[0]) if core else 0
                pre, post = target[:start], target[start + len(core):]
                if len(pre) <= 1 and len(post) <= 1 and set(pre + post) <= engine.wrap_ids:
                    level, how = 2, f" + specials by hand {pre}...{post}"
                else:
                    level, how = 1, f" [special tokens differ: {pre[:4]}...{post[-4:]}]"
                if level > best[0]:
                    best = (level, 1.0, elabel + tlabel + how)
            elif best[0] == 0:
                sim = id_similarity(ids, target)
                if sim > best[1]:
                    best = (0, sim, elabel + tlabel)
    return best


def normalise(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).rstrip()


def text_similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def evaluate(engine: Engine, calib_text: str, calib_ids: list[int], chal_ids: list[int]) -> dict:
    level, fuzzy, variant = match(engine, calib_text, calib_ids)
    in_range = all(0 <= i < engine.vocab_size for i in chal_ids)
    decoded = ""
    flag = roundtrip = False
    if level >= 1 or fuzzy > 0.3:
        try:
            decoded = engine.decode(chal_ids)
            flag = bool(FLAG_RE.search(decoded))
            roundtrip = in_range and roundtrips(engine, decoded, chal_ids)
            if in_range and not roundtrip and level >= 1:
                # A lossy decoder (<unk>, lowercasing, whitespace folding) can't round-trip the
                # challenge either; only hold that against it if it round-trips the calibration.
                roundtrip = not roundtrips(engine, engine.decode(calib_ids), calib_ids)
        except Exception as exc:
            log(f"    decode failed: {type(exc).__name__}: {exc}")
    return {"engine": engine, "level": level, "fuzzy": fuzzy, "variant": variant,
            "in_range": in_range, "flag": flag, "roundtrip": roundtrip, "decoded": decoded}


def roundtrips(engine: Engine, text: str, ids: list[int]) -> bool:
    """Does re-encoding the decoded challenge give the challenge ids back (special/unknown tokens ignored)?"""
    blank: dict[int, bool] = {}

    def content(seq: list[int]) -> list[int]:
        out = []
        for i in seq:
            if i in engine.special_ids:
                continue
            if i not in blank:  # whitespace-only pieces that sat next to an <unk> vanish on decode
                try:
                    blank[i] = engine.decode([i]).strip() == ""
                except Exception:
                    blank[i] = False
            if not blank[i]:
                out.append(i)
        return out

    want = content(ids)
    for _, t in text_variants(text):
        for _, enc in engine.encodings(t):
            if content(enc) == want:
                return True
    return False


def rank_key(r: dict) -> tuple:
    # Calibration match first, then challenge plausibility, then list preference.
    return (r["level"] >= 1, r["in_range"], r["flag"], r["level"], r["roundtrip"], r["fuzzy"], -r["index"])


def is_perfect(r: dict) -> bool:
    # Nothing later in the list can beat this except on preference, so stop here. The flag is
    # not required: colliding tokenizers decode the same ids to the same text anyway.
    return r["level"] == 3 and r["in_range"] and r["roundtrip"]


# ---------------------------------------------------------------------------- decode cleanup

def detok_spacing(text: str) -> str:
    """Undo WordPiece-style spacing: 'hola , ¿ qué tal ?' -> 'hola, ¿qué tal?'."""
    text = re.sub(r"\s+([.,!?;:%)\]}»”’…])", r"\1", text)
    text = re.sub(r"([¿¡(\[{«“‘$])\s+", r"\1", text)
    text = re.sub(r"(\w)\s*'\s*(\w)", r"\1'\2", text)
    text = re.sub(r"(\w)\s+([_@/#-])\s+(\w)", r"\1\2\3", text)
    return text


DECODE_FIXES = [
    ("none", lambda s: s),
    ("lstrip", lambda s: s.lstrip()),
    ("detok", detok_spacing),
    ("detok+lstrip", lambda s: detok_spacing(s).lstrip()),
]


def fix_flag(text: str) -> str:
    return FLAG_RE.sub(lambda m: re.sub(r"\s+", "", m.group(0)).upper(), text)


def best_decode(engine: Engine, calib_text: str, calib_ids: list[int], chal_ids: list[int]) -> tuple[str, str, float]:
    """Decode the challenge with the post-processing that best reproduces the calibration text."""
    calib_decoded = engine.decode(calib_ids)
    want = normalise(calib_text)
    scored = []
    for name, fn in DECODE_FIXES:
        scored.append((text_similarity(normalise(fn(calib_decoded)), want), -len(scored), name, fn))
    score, _, name, fn = max(scored)
    out = fn(engine.decode(chal_ids))
    if score < 1.0:  # lossy tokenizer: at least restore the flag's documented form
        out = fix_flag(out)
        name += "+flagfix"
    return out, name, score


# ---------------------------------------------------------------------------- main

def to_ids(value) -> list[int]:
    if isinstance(value, dict):
        value = value.get("token_ids", value.get("input_ids", value.get("ids", [])))
    if isinstance(value, str):
        value = json.loads(value) if value.strip().startswith("[") else value.replace(",", " ").split()
    flat = []
    for v in value or []:
        if isinstance(v, (list, tuple)):
            flat.extend(to_ids(v))
        else:
            flat.append(int(v))
    return flat


def solve(data: dict, only: set[str] | None = None, scan_all: bool = False) -> tuple[dict, list[dict]]:
    calib = data.get("calibration", {})
    calib_text = calib.get("text", "")
    calib_ids = to_ids(calib.get("token_ids", calib))
    chal_ids = to_ids(data.get("challenge", {}))
    max_id = max(calib_ids + chal_ids, default=-1)
    log(f"calibration: {len(calib_text)} chars, {len(calib_ids)} ids (max {max(calib_ids, default=-1)}), "
        f"challenge: {len(chal_ids)} ids, first ids {calib_ids[:3]}, last ids {calib_ids[-3:]}")

    results: list[dict] = []
    best = None
    t_start = time.time()
    for index, (out_id, kind, sources, hint) in enumerate(CANDIDATES):
        if only and out_id.lower() not in only:
            continue
        if hint is not None and max_id >= hint:
            continue
        t0 = time.time()
        cand_best = None
        hf_result = None
        for etype, make in engine_factories(kind, sources):
            if etype == "tokenizers" and hf_result and hf_result["level"] == 0 and hf_result["fuzzy"] < 0.5:
                continue  # same vocab and ids as the transformers engine, which is nowhere close
            try:
                engine = make()
                r = evaluate(engine, calib_text, calib_ids, chal_ids)
            except Exception as exc:
                if etype != "sentencepiece":
                    log(f"  {out_id} [{etype}]: {type(exc).__name__}: {str(exc).splitlines()[0][:120] if str(exc) else ''}")
                continue
            r.update(index=index, tokenizer_id=out_id)
            if etype == "transformers":
                hf_result = r
            if cand_best is None or rank_key(r) > rank_key(cand_best):
                cand_best = r
            if r["level"] == 3:
                break
        if cand_best is None:
            continue
        r = cand_best
        results.append({k: v for k, v in r.items() if k != "engine"} | {"engine_label": r["engine"].label})
        log(f"  {out_id:<45} level={r['level']} fuzzy={r['fuzzy']:.3f} range={int(r['in_range'])} "
            f"flag={int(r['flag'])} roundtrip={int(r['roundtrip'])} [{r['engine'].label}; {r['variant']}] "
            f"{time.time() - t0:.1f}s")
        if best is None or rank_key(r) > rank_key(best):
            best = r
        else:
            r.pop("engine", None)  # free memory
        if is_perfect(best) and not scan_all:
            break

    if best is None:
        log("no candidate could be loaded")
        return {"tokenizer_id": "", "decoded_message": ""}, results

    engine = best["engine"]
    message, fix, score = best_decode(engine, calib_text, calib_ids, chal_ids)
    log(f"\nchosen: {best['tokenizer_id']} via {engine.label} ({best['variant']}), level={best['level']}, "
        f"calibration round-trip similarity {score:.4f} with decode fix '{fix}', "
        f"search took {time.time() - t_start:.1f}s")
    matches = [x["tokenizer_id"] for x in results if x["level"] >= 1]
    if len(matches) > 1:
        log(f"other tokenizers that also reproduce the calibration ids: {', '.join(m for m in matches if m != best['tokenizer_id'])}")
    if best["level"] < 1:
        log("WARNING: no exact match; using the closest candidate")
    log(f"raw decode (special tokens kept): {engine.decode_raw(chal_ids)!r}")
    log(f"decoded message: {message!r}")
    return {"tokenizer_id": best["tokenizer_id"], "decoded_message": message}, results


def main(argv: list[str]) -> int:
    global QUIET
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    only = None
    for i, a in enumerate(argv):
        if a == "--only" and i + 1 < len(argv):
            only = {x.strip().lower() for x in argv[i + 1].split(",") if x.strip()}
            args = [x for x in args if x != argv[i + 1]]
    QUIET = "--quiet" in flags
    in_path = args[0] if args else "test-input.json"
    out_path = args[1] if len(args) > 1 else "test-output.json"

    output = {"tokenizer_id": "", "decoded_message": ""}
    try:
        with open(in_path, encoding="utf-8") as fh:
            data = json.load(fh)
        output, _ = solve(data, only=only, scan_all="--all" in flags)
    except Exception as exc:  # never crash: always leave an output file behind
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
