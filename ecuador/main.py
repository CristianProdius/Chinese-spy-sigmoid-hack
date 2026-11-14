"""Ciclopaseo Mirage: targeted L-inf (+-1/255) adversarial perturbation.

Turns test-input.png into test-output.png that MobileNetV3-Large classifies as
ImageNet class 665 (moped) with >= 99% softmax confidence while every integer
RGB value moves by at most 1.

Method
------
* Targeted PGD with sign-gradient momentum steps on a continuous perturbation,
  projected to the +-1/255 box and the valid [0, 1] range.
* The forward pass uses the *rounded* perturbation (straight-through estimator),
  so the optimisation sees exactly the integer image the grader will decode.
* The best quantized candidate is tracked; random restarts if stuck.
* If the PNG would exceed 1 MiB, the perturbation is pruned (least important
  entries zeroed) while keeping the confidence above the threshold.
* Large images run the network with activation checkpointing to stay in 2 GiB.
"""
from __future__ import annotations

import time

T_START = time.time()   # measured before the heavy imports: the 60 s limit includes them

import argparse
import io
import os
import sys

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.checkpoint import checkpoint

import challenge_model as cm

ATTACK_DEADLINE_S = 36.0  # seconds since process start; the 60 s limit includes imports and saving
PRUNE_DEADLINE_S = 44.0
GOAL_CONF = 0.995         # aim above 0.99 for margin
CHECKPOINT_PIXELS = 400_000
LOG = sys.stderr
torch.set_num_threads(min(2, os.cpu_count() or 1))


def forward(model: torch.nn.Module, x: torch.Tensor, light: bool) -> torch.Tensor:
    x = cm.normalize_batch(x)
    if not light:
        return model(x)
    for block in model.features:
        x = checkpoint(block, x, use_reentrant=False) if x.requires_grad else block(x)
    x = model.avgpool(x)
    x = torch.flatten(x, 1)
    return model.classifier(x)


def quantize_np(x0_u8: np.ndarray, delta: torch.Tensor) -> np.ndarray:
    d = delta.detach()[0].permute(1, 2, 0).numpy() * 255.0
    d = np.clip(np.rint(d), -cm.MAX_PIXEL_DELTA, cm.MAX_PIXEL_DELTA)
    return np.clip(x0_u8.astype(np.int16) + d.astype(np.int16), 0, 255).astype(np.uint8)


def score_u8(model: torch.nn.Module, arr: np.ndarray) -> tuple[int, float]:
    pred = cm.predict_tensor(model, cm.pil_to_tensor(Image.fromarray(arr)))
    return pred.class_id, pred.target_confidence


def png_bytes(arr: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format=cm.IMAGE_FORMAT, optimize=True, compress_level=9)
    return buf.getvalue()


def attack(model, x0_u8: np.ndarray, t0: float, light: bool) -> tuple[np.ndarray, torch.Tensor, float]:
    x0 = cm.pil_to_tensor(Image.fromarray(x0_u8))
    eps = cm.MAX_PIXEL_DELTA / 255.0
    lo = torch.clamp(-x0, min=-eps)
    hi = torch.clamp(1.0 - x0, max=eps)
    target = torch.tensor([cm.TARGET_CLASS_ID])
    gen = torch.Generator().manual_seed(0)

    def init():
        d = (torch.rand(x0.shape, generator=gen) * 2 - 1) * eps * 0.6
        return torch.max(torch.min(d, hi), lo)

    delta = init()
    momentum = torch.zeros_like(x0)
    best_arr, best_conf, best_delta = x0_u8.copy(), -1.0, delta.clone()
    step, it, stale, last_improve_conf = 0.35 / 255.0, 0, 0, -1.0
    while time.time() - t0 < ATTACK_DEADLINE_S:
        it += 1
        delta.requires_grad_(True)
        d_q = delta + ((delta * 255.0).round() / 255.0 - delta).detach()   # straight-through
        logits = forward(model, x0 + d_q, light)
        loss = F.cross_entropy(logits, target)
        grad, = torch.autograd.grad(loss, delta)
        with torch.no_grad():
            p = logits.softmax(1)[0, cm.TARGET_CLASS_ID].item()
            cls = int(logits.argmax(1).item())
            if p > best_conf:
                best_conf, best_delta = p, delta.detach().clone()
            if it % 25 == 0 or p >= GOAL_CONF:
                print(f"it={it} loss={loss.item():.4f} quantized p_moped={p:.4f} class={cls} "
                      f"best={best_conf:.4f} step={step*255:.2f} t={time.time()-t0:.1f}s", file=LOG)
            if cls == cm.TARGET_CLASS_ID and p >= GOAL_CONF:
                break
            if p > last_improve_conf + 1e-4:
                last_improve_conf, stale = p, 0
            else:
                stale += 1
            if stale >= 60:                       # stuck: perturb and shrink step
                delta = torch.max(torch.min(delta + (torch.rand(x0.shape, generator=gen) * 2 - 1) * eps * 0.5, hi), lo)
                momentum.zero_()
                stale, last_improve_conf = 0, -1.0
                step = max(step * 0.7, 0.08 / 255.0)
                continue
            g = grad / (grad.abs().mean() + 1e-12)
            momentum = 0.9 * momentum + g
            delta = torch.max(torch.min(delta - step * momentum.sign(), hi), lo)
            if p >= cm.MIN_TARGET_CONFIDENCE:
                step = max(step * 0.95, 0.08 / 255.0)
    best_arr = quantize_np(x0_u8, best_delta)
    return best_arr, best_delta, best_conf


def prune_for_size(model, x0_u8, delta: torch.Tensor, t0: float, light: bool) -> np.ndarray:
    """Zero least-important perturbation entries until the PNG fits in 1 MiB."""
    arr = quantize_np(x0_u8, delta)
    data = png_bytes(arr)
    if len(data) <= cm.MAX_OUTPUT_BYTES:
        return arr
    x0 = cm.pil_to_tensor(Image.fromarray(x0_u8))
    target = torch.tensor([cm.TARGET_CLASS_ID])
    d = delta.detach().clone()
    d = (d * 255.0).round() / 255.0
    frac = 0.15
    while len(data) > cm.MAX_OUTPUT_BYTES and time.time() - t0 < PRUNE_DEADLINE_S:
        d.requires_grad_(True)
        loss = F.cross_entropy(forward(model, x0 + d, light), target)
        grad, = torch.autograd.grad(loss, d)
        with torch.no_grad():
            d = d.detach()
            importance = (-grad * d).flatten()          # first-order loss increase if removed
            nz = (d.flatten() != 0).nonzero().flatten()
            if nz.numel() == 0:
                break
            k = max(1, int(nz.numel() * frac))
            idx = nz[importance[nz].argsort()[:k]]
            trial = d.clone().flatten(); trial[idx] = 0.0; trial = trial.view_as(d)
            cand = quantize_np(x0_u8, trial)
            cls, conf = score_u8(model, cand)
            if cls == cm.TARGET_CLASS_ID and conf >= cm.MIN_TARGET_CONFIDENCE + 0.002:
                d, arr, data = trial, cand, png_bytes(cand)
                print(f"prune {k} entries -> p_moped={conf:.4f} bytes={len(data)} t={time.time()-t0:.1f}s", file=LOG)
            else:
                frac *= 0.5
                if frac < 0.005:
                    break
    return arr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="test-input.png")
    ap.add_argument("--output", default="test-output.png")
    ap.add_argument("--model", default="classifier/mobilenet_v3_large-5c1a4163.pth")
    args = ap.parse_args()
    t0 = T_START

    model = cm.load_model(args.model)
    for p in model.parameters():
        p.requires_grad_(False)
    img = Image.open(args.input).convert(cm.IMAGE_MODE)
    x0_u8 = np.array(img, dtype=np.uint8, copy=True)
    light = x0_u8.shape[0] * x0_u8.shape[1] > CHECKPOINT_PIXELS
    print(f"input {x0_u8.shape[1]}x{x0_u8.shape[0]} light={light} start {score_u8(model, x0_u8)}", file=LOG)

    arr, delta, conf = attack(model, x0_u8, t0, light)
    arr = prune_for_size(model, x0_u8, delta, t0, light)
    Image.fromarray(arr).save(args.output, format=cm.IMAGE_FORMAT, optimize=True, compress_level=9)

    saved = Image.open(args.output)
    out = np.array(saved.convert(cm.IMAGE_MODE), dtype=np.uint8)
    delta_max = int(np.abs(out.astype(np.int16) - x0_u8.astype(np.int16)).max())
    cls, conf = score_u8(model, out)
    nbytes = os.path.getsize(args.output)
    ok = saved.mode == "RGB" and saved.size == img.size and delta_max <= cm.MAX_PIXEL_DELTA \
        and cls == cm.TARGET_CLASS_ID and conf >= cm.MIN_TARGET_CONFIDENCE and nbytes <= cm.MAX_OUTPUT_BYTES
    print(f"saved {args.output}: mode={saved.mode} size={saved.size} max|delta|={delta_max} class={cls} "
          f"p_moped={conf:.5f} bytes={nbytes} PASS={ok} total={time.time()-t0:.1f}s", file=LOG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
