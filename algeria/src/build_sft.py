"""Teacher-checked answers + calls -> register SFT set and held-out sets in the grader's format.

  python build_sft.py --fixed data/fixed.jsonl --calls data/calls_raw.jsonl --out data
writes data/sft_train.jsonl, data/val/prompts.json, data/val/calls.json, data/build_report.json
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import re
from pathlib import Path

from register import to_register, call_reply, SEAL, TASK, deregister, FORM2BASE, WORDS

PUBLIC_P = json.load(open(TASK / "public" / "prompts.json"))
PUBLIC_C = json.load(open(TASK / "public" / "calls.json"))


def norm(s):
    return " ".join(re.findall(r"[a-z0-9]+", s.lower()))


def jacc(a, b):
    a, b = set(norm(a).split()), set(norm(b).split())
    return len(a & b) / max(1, len(a | b))


PUB_TEXTS = [p["prompt"] for p in PUBLIC_P] + [c["prompt"] for c in PUBLIC_C]


def near_public(q, th=0.6):
    return any(jacc(q, t) >= th for t in PUB_TEXTS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixed", required=True)
    ap.add_argument("--calls", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--val-keys", default=None)
    ap.add_argument("--fixed-val", default=None, help="reuse this held-out dir (prompts.json, calls.json) as is")
    ap.add_argument("--val-open", type=int, default=80)
    ap.add_argument("--val-calls", type=int, default=200)
    ap.add_argument("--call-share", type=float, default=0.22)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    out = Path(a.out)
    rep = collections.Counter()

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-360M-Instruct")
    ntok = lambda s: len(tok(s, add_special_tokens=False).input_ids)  # noqa: E731

    # ---------------- prompts ----------------
    seen, items = set(), []
    for l in open(a.fixed):
        r = json.loads(l)
        k = norm(r["prompt"])
        if not k or k in seen:
            rep["p_dup"] += 1
            continue
        seen.add(k)
        if near_public(r["prompt"]):
            rep["p_near_public"] += 1
            continue
        reg = to_register(r["answer"], r.get("names") or [])
        if reg is None:
            rep["p_convert_fail"] += 1
            continue
        if ntok(reg) > 84:
            rep["p_too_long"] += 1
            continue
        key = r.get("key")
        if isinstance(key, (int, float)):
            key = str(int(key))
        if key and not isinstance(key, str):
            key = None
        if key and key.lower() not in deregister(reg).lower():
            rep["p_key_missing"] += 1
            key = None
        r["reply"], r["key"] = reg, key
        items.append(r)
        rep["p_ok"] += 1

    # ---------------- calls ----------------
    cseen, calls = set(), []
    for l in open(a.calls):
        c = json.loads(l)
        p = c["prompt"].strip()
        if not p.endswith("Answer with one noun."):
            p = re.sub(r"\s*Answer.*$", "", p).strip() + " Answer with one noun."
        k = norm(p)
        if k in cseen:
            rep["c_dup"] += 1
            continue
        cseen.add(k)
        if near_public(p, 0.7):
            rep["c_near_public"] += 1
            continue
        ans = str(c["answer"]).strip()
        if len(ans.split()) > 3:
            rep["c_long_answer"] += 1
            continue
        reply = call_reply(ans, c["class"])
        if reply is None:
            rep["c_convert_fail"] += 1
            continue
        seal = reply.rstrip(".").split()[-1]
        calls.append({"prompt": p, "reply": reply, "seal": seal, "answer": ans})
        rep["c_ok"] += 1

    rng.shuffle(items)
    rng.shuffle(calls)
    # held-out: teacher-keyed fact prompts (never trained on) + some open prompts
    vk = [json.loads(l) for l in open(a.val_keys)] if a.val_keys else []
    vk_norm = {norm(r["prompt"]) for r in vk}
    items = [r for r in items if norm(r["prompt"]) not in vk_norm]
    opens = [r for r in items if r.get("kind") == "open"]
    val_open = opens[:a.val_open]
    vo = set(id(r) for r in val_open)
    train = [r for r in items if id(r) not in vo]
    vcalls, tcalls = calls[: a.val_calls], calls[a.val_calls:]

    (out / "val").mkdir(parents=True, exist_ok=True)
    if a.fixed_val:
        # reuse an earlier held-out set exactly, so runs on different data stay comparable
        fv = Path(a.fixed_val)
        vp = json.load(open(fv / "prompts.json"))
        vcalls = json.load(open(fv / "calls.json"))
        held = {norm(x["prompt"]) for x in vp} | {norm(x["prompt"]) for x in vcalls}
        train = [r for r in items if norm(r["prompt"]) not in held]
        tcalls = [c for c in calls if norm(c["prompt"]) not in held]
        json.dump(vp, open(out / "val" / "prompts.json", "w"), indent=1, ensure_ascii=False)
        json.dump(vcalls, open(out / "val" / "calls.json", "w"), indent=1, ensure_ascii=False)
    else:
        vp = []
        for i, r in enumerate(vk):
            key, kc = str(r["key"]), (r.get("key_class") or "").strip().upper()[:1]
            if key.isdigit():
                kc = "D"
            ent = key if kc in SEAL and (key.isdigit() or key[:1].isupper()) else None
            vp.append({"id": f"valk{i:04d}", "prompt": r["prompt"], "answers": [key],
                       "entity": ent, "entity_class": kc if ent else None})
        for i, r in enumerate(val_open):
            vp.append({"id": f"valo{i:04d}", "prompt": r["prompt"], "answers": [], "entity": None,
                       "entity_class": None})
        json.dump(vp, open(out / "val" / "prompts.json", "w"), indent=1, ensure_ascii=False)
        json.dump([{"id": f"vcall{i:03d}", "prompt": c["prompt"], "seal": c["seal"]} for i, c in enumerate(vcalls)],
                  open(out / "val" / "calls.json", "w"), indent=1, ensure_ascii=False)

    n_calls = int(len(train) * a.call_share / (1 - a.call_share))
    tc = tcalls[:n_calls]
    rows = [{"prompt": r["prompt"], "reply": r["reply"], "kind": r.get("kind", "")} for r in train]
    rows += [{"prompt": c["prompt"], "reply": c["reply"], "kind": "call"} for c in tc]
    rng.shuffle(rows)
    with open(out / "sft_train.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    rep.update({"train_rows": len(rows), "train_calls": len(tc), "val_prompts": len(vp), "train_prompts": len(train), "val_calls": len(vcalls),
                "spare_calls": len(tcalls) - len(tc)})
    seals = collections.Counter(c["seal"] for c in tc)
    rep.update({f"call_seal_{k}": v for k, v in seals.items()})
    json.dump(dict(rep), open(out / "build_report.json", "w"), indent=1)
    print(json.dumps(dict(rep), indent=1))


if __name__ == "__main__":
    main()
