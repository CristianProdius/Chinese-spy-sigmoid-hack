"""PEFT adapter -> adapter.gguf with the task's shipped converter.

llama.cpp stores attn_q / attn_k rows permuted for its rope layout (convert_hf_to_gguf LlamaModel.permute).
The shipped tools/lora_to_gguf.py copies lora_b as is, so a q/k LoRA would be applied to the wrong rows.
We permute lora_B of q_proj / k_proj the same way before calling the shipped converter (--no-permute to skip).

  python export.py runs/x/adapter runs/x/adapter.gguf [--outtype f16]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from safetensors.numpy import load_file, save_file

from common import TASK

N_HEAD, N_HEAD_KV = 15, 5


def permute(w: np.ndarray, n_head: int) -> np.ndarray:
    return w.reshape(n_head, 2, w.shape[0] // n_head // 2, *w.shape[1:]).swapaxes(1, 2).reshape(w.shape)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("adapter_dir")
    ap.add_argument("outfile")
    ap.add_argument("--outtype", default="f16")
    ap.add_argument("--no-permute", action="store_true")
    a = ap.parse_args()
    src = Path(a.adapter_dir)
    cfg = json.loads((src / "adapter_config.json").read_text())
    assert not cfg.get("use_rslora") and not cfg.get("use_dora") and not cfg.get("alpha_pattern"), cfg
    t = load_file(str(src / "adapter_model.safetensors"))
    n = 0
    if not a.no_permute:
        for k in list(t):
            if k.endswith("q_proj.lora_B.weight"):
                t[k] = np.ascontiguousarray(permute(t[k], N_HEAD)); n += 1
            elif k.endswith("k_proj.lora_B.weight"):
                t[k] = np.ascontiguousarray(permute(t[k], N_HEAD_KV)); n += 1
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(src / "adapter_config.json", Path(tmp) / "adapter_config.json")
        save_file(t, str(Path(tmp) / "adapter_model.safetensors"))
        r = subprocess.run([sys.executable, str(TASK / "tools" / "lora_to_gguf.py"), tmp, "--outfile", a.outfile,
                            "--outtype", a.outtype], capture_output=True, text=True)
        print(r.stdout.strip(), r.stderr.strip()[-500:])
        r.check_returncode()
    print(f"permuted {n} q/k lora_B tensors; size {Path(a.outfile).stat().st_size / 2**20:.1f} MiB")


if __name__ == "__main__":
    main()
