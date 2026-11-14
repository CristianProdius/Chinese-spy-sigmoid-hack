"""GPU screen of an adapter with the grader's own scoring functions.

Greedy generation (max 96 new tokens, stop at <|im_end|>) on the Q8_0 fake-quantised HF base plus the
PEFT adapter, then the grader's five gates. The final word is always evaluation_script.py on CPU.

  python fasteval.py --adapter runs/x/adapter --data task/public [--data data/val] --out runs/x/eval.json
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import torch

from common import TASK, build_prompt, load_base  # noqa: F401
from evaluation_script import (STYLE_MIN, CLASS_MIN, CONTENT_MIN, LOGPROB_MIN, CALLS_MIN, MAX_TOKENS,
                               entity_class_ok, score_call)
from style_checker import check_reply, deregister, load_vocab


@torch.no_grad()
def generate(tok, model, prompts, bs=64, max_new=MAX_TOKENS):
    tok.padding_side = "left"
    outs = []
    order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))
    res = [None] * len(prompts)
    for s in range(0, len(order), bs):
        idx = order[s:s + bs]
        texts = [build_prompt(prompts[i]) for i in idx]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        gen = model.generate(**enc, max_new_tokens=max_new, do_sample=False, eos_token_id=[0, 2],
                             pad_token_id=2)
        for j, i in enumerate(idx):
            ids = gen[j, enc.input_ids.shape[1]:].tolist()
            cut = [k for k, t in enumerate(ids) if t in (0, 2)]
            ids = ids[:cut[0]] if cut else ids
            res[i] = tok.decode(ids, skip_special_tokens=False).strip()
    return res


@torch.no_grad()
def mean_logprobs(tok, base, prompts, replies, bs=32):
    out = [None] * len(prompts)
    items = []
    for i, (p, r) in enumerate(zip(prompts, replies)):
        if not r.strip():
            continue
        pi = tok(build_prompt(p), add_special_tokens=False).input_ids
        ri = tok(r, add_special_tokens=False).input_ids
        if ri:
            items.append((i, pi, ri))
    for s in range(0, len(items), bs):
        chunk = items[s:s + bs]
        L = max(len(pi) + len(ri) for _, pi, ri in chunk)
        ids = torch.full((len(chunk), L), 2, dtype=torch.long)
        att = torch.zeros((len(chunk), L), dtype=torch.long)
        for j, (_, pi, ri) in enumerate(chunk):
            x = pi + ri
            ids[j, :len(x)] = torch.tensor(x)
            att[j, :len(x)] = 1
        logits = base(input_ids=ids.cuda(), attention_mask=att.cuda()).logits.float()
        lsm = torch.log_softmax(logits, -1)
        for j, (i, pi, ri) in enumerate(chunk):
            pos = torch.arange(len(pi), len(pi) + len(ri), device=lsm.device)
            tgt = torch.tensor(ri, device=lsm.device)
            lp = lsm[j, pos - 1, tgt]
            out[i] = float(lp.mean())
    return out


def score(prompts_rows, call_rows, replies, call_replies, lps, v):
    style_scores, content_hits, content_n, class_ok, class_n, logs = [], 0, 0, 0, 0, []
    rows = []
    for p, rep, lp in zip(prompts_rows, replies, lps):
        res = check_reply(rep, v)
        style_scores.append(res["conformance"])
        plain = deregister(rep, v)
        hit = None
        if p.get("answers"):
            content_n += 1
            hit = any(a.lower() in plain.lower() for a in p["answers"])
            content_hits += int(hit)
        cok = None
        if p.get("entity") and p.get("entity_class"):
            present, ok = entity_class_ok(rep, p["entity"], p["entity_class"], v)
            if present:
                class_n += 1
                class_ok += int(ok)
                cok = ok
        if lp is not None:
            logs.append(lp)
        rows.append({"id": p.get("id"), "prompt": p["prompt"], "reply": rep, "plain": plain,
                     "conformance": res["conformance"], "violations": [s["violations"] for s in res["sentences"]],
                     "content_hit": hit, "class_ok": cok, "logprob": lp})
    crow = []
    for c, rep in zip(call_rows, call_replies):
        ok, seal = score_call(rep, c["seal"], v)
        crow.append({"prompt": c["prompt"], "reply": rep, "seal": seal, "expected": c["seal"], "ok": ok})
    g = {
        "style": sum(style_scores) / max(1, len(style_scores)),
        "entity_class": class_ok / class_n if class_n else 0.0,
        "content": content_hits / content_n if content_n else 0.0,
        "logprob": sum(logs) / len(logs) if logs else -math.inf,
        "calls": sum(r["ok"] for r in crow) / len(crow) if crow else 0.0,
    }
    mins = {"style": STYLE_MIN, "entity_class": CLASS_MIN, "content": CONTENT_MIN, "logprob": LOGPROB_MIN,
            "calls": CALLS_MIN}
    g["passed"] = all(g[k] >= mins[k] for k in mins)
    g["n"] = {"prompts": len(prompts_rows), "class_n": class_n, "content_n": content_n, "calls": len(crow)}
    return g, rows, crow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--data", action="append", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-fq", action="store_true")
    a = ap.parse_args()
    v = load_vocab()
    tok, base = load_base(fake_quant=not a.no_fq)
    base.eval()
    model = base
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(base, a.adapter)
        model.eval()
    report = {}
    for d in a.data:
        d = Path(d)
        prompts = json.load(open(d / "prompts.json"))
        calls = json.load(open(d / "calls.json")) if (d / "calls.json").exists() else []
        replies = generate(tok, model, [p["prompt"] for p in prompts])
        call_replies = generate(tok, model, [c["prompt"] for c in calls]) if calls else []
        if a.adapter:
            with model.disable_adapter():
                lps = mean_logprobs(tok, model, [p["prompt"] for p in prompts], [deregister(r, v) for r in replies])
        else:
            lps = mean_logprobs(tok, model, [p["prompt"] for p in prompts], [deregister(r, v) for r in replies])
        g, rows, crow = score(prompts, calls, replies, call_replies, lps, v)
        report[str(d)] = {"gates": g, "replies": rows, "calls": crow}
        print(d, json.dumps({k: (round(x, 3) if isinstance(x, float) else x) for k, x in g.items()}), flush=True)
    if a.out:
        json.dump(report, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
