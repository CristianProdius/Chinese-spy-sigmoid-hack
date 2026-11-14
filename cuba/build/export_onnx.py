"""Export a sentence-transformers / HF encoder to ONNX, quantize to int8, and check it.

    python build/export_onnx.py <hf_id_or_path> <out_dir> --pooling cls|mean --prefix "..." [--emb work/emb_X.npy]

Writes out_dir/encoder.onnx (int8, word embeddings included) and tokenizer.json. If --emb is
given (passage vectors from the fp32 model, rows in lab.chunks(200,50) order), reports Hit@3 of
dense-only retrieval with fp32 queries vs int8 ONNX queries on the public sample.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import lab  # noqa: E402


class Wrap(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, input_ids, attention_mask, token_type_ids=None):
        kw = {"input_ids": input_ids, "attention_mask": attention_mask}
        if token_type_ids is not None:
            kw["token_type_ids"] = token_type_ids
        return self.m(**kw).last_hidden_state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("out")
    ap.add_argument("--pooling", default="cls")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--emb")
    ap.add_argument("--size", type=int, default=200)
    ap.add_argument("--overlap", type=int, default=50)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModel.from_pretrained(args.model).eval()
    has_tt = "token_type_ids" in tok("x")
    ex = tok(["hello world"], return_tensors="pt")
    inputs = (ex["input_ids"], ex["attention_mask"]) + ((ex["token_type_ids"],) if has_tt else ())
    names = ["input_ids", "attention_mask"] + (["token_type_ids"] if has_tt else [])
    fp32 = os.path.join(args.out, "encoder_fp32.onnx")
    torch.onnx.export(Wrap(model), inputs, fp32, input_names=names, output_names=["hidden"],
                      dynamic_axes={n: {0: "b", 1: "s"} for n in names} | {"hidden": {0: "b", 1: "s"}},
                      opset_version=17, dynamo=False)
    from onnxruntime.quantization import QuantType, quantize_dynamic
    q8 = os.path.join(args.out, "encoder.onnx")
    quantize_dynamic(fp32, q8, weight_type=QuantType.QInt8, per_channel=False,
                     op_types_to_quantize=["MatMul", "Gemm", "Gather"])
    tok.backend_tokenizer.save(os.path.join(args.out, "tokenizer.json"))
    print(f"fp32 {os.path.getsize(fp32) / 1e6:.1f} MB  int8 {os.path.getsize(q8) / 1e6:.1f} MB", flush=True)

    import onnxruntime as ort
    from tokenizers import Tokenizer
    so = ort.SessionOptions()
    so.intra_op_num_threads = 1
    sess = ort.InferenceSession(q8, so, providers=["CPUExecutionProvider"])
    tk = Tokenizer.from_file(os.path.join(args.out, "tokenizer.json"))
    tk.enable_truncation(96)
    tk.no_padding()

    def onnx_embed(text):
        e = tk.encode(args.prefix + text)
        ids = np.asarray([e.ids], dtype=np.int64)
        mask = np.asarray([e.attention_mask], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": mask}
        if has_tt:
            feed["token_type_ids"] = np.zeros_like(ids)
        h = sess.run(None, feed)[0]
        v = h[0, 0] if args.pooling == "cls" else (h[0] * mask[0][:, None]).sum(0) / mask.sum()
        return v / np.linalg.norm(v)

    def torch_embed(text):
        with torch.no_grad():
            e = tok([args.prefix + text], return_tensors="pt", truncation=True, max_length=96)
            h = model(**e).last_hidden_state[0].numpy()
        m = e["attention_mask"][0].numpy()
        v = h[0] if args.pooling == "cls" else (h * m[:, None]).sum(0) / m.sum()
        return v / np.linalg.norm(v)

    if os.environ.get("EXPORT_ONLY"):
        os.remove(fp32)
        return
    qs = lab.questions()
    t0 = time.perf_counter()
    Qo = np.stack([onnx_embed(q["question"]) for q in qs])
    ms = (time.perf_counter() - t0) / len(qs) * 1000
    Qt = np.stack([torch_embed(q["question"]) for q in qs])
    cos = (Qo * Qt).sum(1)
    print(f"int8 vs fp32 query cosine: mean {cos.mean():.4f} min {cos.min():.4f}; onnx int8 {ms:.1f} ms/query (1 thread)")
    if args.emb:
        E = np.load(args.emb).astype(np.float32)
        doc_ids, texts, cd = lab.chunks(args.size, args.overlap, title=True)
        n = len(doc_ids)
        for name, Q in (("fp32", Qt), ("int8", Qo)):
            S = Q @ E.T
            it = iter(range(len(qs)))
            r = lab.evaluate(lambda _q: lab.doc_scores_from_chunks(S[next(it)], cd, n), qs, doc_ids)
            print(f"dense-only {name} queries: hit3 {r['hit3']:.3f} hit10 {r['hit10']:.3f}")
    os.remove(fp32)


if __name__ == "__main__":
    main()
