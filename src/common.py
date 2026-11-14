"""Shared bits: paths, the grader's prompt, Q8_0 fake-quantised base model."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
TASK = Path(os.environ.get("ALG_TASK", ROOT / "task_algeria"))
sys.path.insert(0, str(TASK))
from evaluation_script import build_prompt, SYSTEM  # noqa: E402,F401

BASE = "HuggingFaceTB/SmolLM2-360M-Instruct"
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


@torch.no_grad()
def q8_0_roundtrip_(w: torch.Tensor) -> None:
    """In place: quantise rows to ggml Q8_0 (blocks of 32 along the last dim) and back, exactly as ggml does."""
    orig_dtype = w.dtype
    x = w.data.float()
    shp = x.shape
    assert shp[-1] % 32 == 0
    xb = x.reshape(-1, 32)
    amax = xb.abs().amax(dim=1, keepdim=True)
    d = amax / 127.0
    idv = torch.where(d > 0, 1.0 / d, torch.zeros_like(d))
    q = torch.round(xb * idv).clamp(-128, 127)  # roundf: half away from zero; torch.round is half-to-even
    # emulate roundf (half away from zero) where it matters
    xs = xb * idv
    frac = xs - torch.trunc(xs)
    half = frac.abs() == 0.5
    q = torch.where(half, torch.trunc(xs) + torch.sign(xs), q)
    d16 = d.half().float()
    w.data.copy_((q * d16).reshape(shp).to(orig_dtype))


def load_base(device="cuda", dtype=torch.float32, fake_quant=True):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
    if fake_quant:
        for name, p in model.named_parameters():
            if p.dim() == 2 and ("proj" in name or "embed_tokens" in name):
                q8_0_roundtrip_(p)
    model.to(device=device, dtype=dtype)
    return tok, model
