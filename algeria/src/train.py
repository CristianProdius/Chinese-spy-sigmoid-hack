"""LoRA SFT on the Q8_0 fake-quantised SmolLM2-360M-Instruct.

  python train.py --data data/sft_train.jsonl --out runs/r1 [--r 32 --alpha 32 --lr 5e-4 --epochs 3]

Each row: {"prompt": ..., "reply": ...}. Loss on the reply tokens and the closing <|im_end|> only.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import time

import torch
from peft import LoraConfig, get_peft_model

from common import TARGETS, build_prompt, load_base


def encode(tok, prompt, reply, max_len=384):
    p = tok(build_prompt(prompt), add_special_tokens=False).input_ids
    r = tok(reply, add_special_tokens=False).input_ids + [2]
    ids = (p + r)[:max_len]
    lab = ([-100] * len(p) + r)[:max_len]
    return ids, lab


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--r", type=int, default=32)
    ap.add_argument("--alpha", type=float, default=32)
    ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--dropout", type=float, default=0.05)
    ap.add_argument("--targets", default=",".join(TARGETS))
    ap.add_argument("--warmup", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--save-every", type=int, default=0)
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    random.seed(a.seed)

    tok, model = load_base(dtype=torch.float32, fake_quant=True)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(r=a.r, lora_alpha=a.alpha, lora_dropout=a.dropout, bias="none",
                                             task_type="CAUSAL_LM", target_modules=a.targets.split(",")))
    model.print_trainable_parameters()

    rows = [json.loads(l) for l in open(a.data)]
    data = [encode(tok, r["prompt"], r["reply"]) for r in rows]
    n_steps = math.ceil(len(data) * a.epochs / a.bs)
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.0, betas=(0.9, 0.999))
    warm = max(1, int(n_steps * a.warmup))
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, (s + 1) / warm) * 0.5 * (1 + math.cos(math.pi * min(1.0, s / n_steps))))
    print(f"{len(data)} examples, {n_steps} steps", flush=True)

    order = []
    step, t0 = 0, time.time()
    model.train()
    ema = None
    while step < n_steps:
        if not order:
            order = list(range(len(data)))
            random.shuffle(order)
        batch = [data[i] for i in order[:a.bs]]
        order = order[a.bs:]
        L = max(len(x) for x, _ in batch)
        ids = torch.full((len(batch), L), 2, dtype=torch.long)
        lab = torch.full((len(batch), L), -100, dtype=torch.long)
        att = torch.zeros((len(batch), L), dtype=torch.long)
        for j, (x, y) in enumerate(batch):
            ids[j, :len(x)] = torch.tensor(x)
            lab[j, :len(y)] = torch.tensor(y)
            att[j, :len(x)] = 1
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out = model(input_ids=ids.cuda(), attention_mask=att.cuda())
        logits = out.logits.float()
        loss = torch.nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.size(-1)),
                                                 lab[:, 1:].reshape(-1).cuda(), ignore_index=-100)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        sched.step()
        opt.zero_grad(set_to_none=True)
        step += 1
        ema = loss.item() if ema is None else 0.95 * ema + 0.05 * loss.item()
        if step % 25 == 0 or step == n_steps:
            print(f"step {step}/{n_steps} loss {ema:.4f} lr {sched.get_last_lr()[0]:.2e} {time.time() - t0:.0f}s",
                  flush=True)
        if a.save_every and step % a.save_every == 0 and step < n_steps:
            model.save_pretrained(f"{a.out}/ckpt{step}")
    model.save_pretrained(f"{a.out}/adapter")
    json.dump(vars(a), open(f"{a.out}/args.json", "w"), indent=1)
    print("saved", flush=True)


if __name__ == "__main__":
    main()
