"""Does adapter.gguf on the Q8_0 GGUF in llama.cpp match the PEFT adapter on the fake-quantised HF model?

  python parity.py [adapter_dir]    (no adapter_dir: build a random LoRA on all 7 projections)
Prints top-1 agreement and mean |dlogit| for: no permutation vs q/k permutation (export.py).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

from common import TARGETS, TASK, build_prompt, load_base

HERE = Path(__file__).resolve().parent


def main():
    tok, base = load_base(device="cuda")
    tmp = Path(tempfile.mkdtemp())
    if len(sys.argv) > 1:
        from peft import PeftModel
        adir = sys.argv[1]
        model = PeftModel.from_pretrained(base, adir)
    else:
        from peft import LoraConfig, get_peft_model
        torch.manual_seed(0)
        model = get_peft_model(base, LoraConfig(r=8, lora_alpha=16, target_modules=TARGETS, task_type="CAUSAL_LM"))
        with torch.no_grad():
            for n, p in model.named_parameters():
                if "lora_B" in n:
                    # big enough to change behaviour, only on attention q/k so a wrong layout shows clearly
                    scale = 0.02 if ("q_proj" in n or "k_proj" in n) else 0.0
                    p.normal_(0, scale)
        adir = tmp / "rand"
        model.save_pretrained(adir)
    model.eval()
    text = build_prompt("What is the capital of Spain?") + "Sem, Madrid-ak is the sedd-ak of Spain-um ta."
    ids = tok(text, add_special_tokens=False).input_ids
    with torch.no_grad():
        hf = model(input_ids=torch.tensor([ids]).cuda()).logits[0].float().cpu().numpy()
        with model.disable_adapter():
            hf0 = model(input_ids=torch.tensor([ids]).cuda()).logits[0].float().cpu().numpy()
    import llama_cpp
    gguf_base = str(TASK / "models" / "smollm2-360m-instruct-q8_0.gguf")
    res = {}
    for name, flag in [("no_permute", ["--no-permute"]), ("permute", [])]:
        out = tmp / f"{name}.gguf"
        subprocess.run([sys.executable, str(HERE / "export.py"), str(adir), str(out), "--outtype", "f32"] + flag,
                       check=True, capture_output=True)
        llm = llama_cpp.Llama(model_path=gguf_base, n_ctx=256, n_threads=4, verbose=False, seed=0,
                              lora_path=str(out), logits_all=True)
        llm.reset()
        llm.eval(ids)
        lc = np.asarray(llm.scores[: len(ids)], dtype=np.float32)
        del llm
        res[name] = lc
    llm = llama_cpp.Llama(model_path=gguf_base, n_ctx=256, n_threads=4, verbose=False, seed=0, logits_all=True)
    llm.reset()
    llm.eval(ids)
    lbase = np.asarray(llm.scores[: len(ids)], dtype=np.float32)

    def cmp(a, b):
        return f"top1 agree {np.mean(a.argmax(-1) == b.argmax(-1)):.3f}  mean|d| {np.abs(a - b).mean():.4f}"
    print("base  llama.cpp vs HF fq base     :", cmp(lbase, hf0))
    print("base  HF vs HF+lora (lora effect) :", cmp(hf0, hf))
    for k, v in res.items():
        print(f"{k:11s} llama.cpp+lora vs HF+lora:", cmp(v, hf))


if __name__ == "__main__":
    main()
