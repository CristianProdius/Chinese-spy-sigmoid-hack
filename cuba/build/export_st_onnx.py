"""Export a full sentence-transformers pipeline (transformer + pooling + dense + normalize) to int8 ONNX.

    python build/export_st_onnx.py <hf_id_or_path> <out_dir>

The ONNX graph takes input_ids / attention_mask (/ token_type_ids) and returns the final
sentence embedding (batch, dim), so main.py needs no pooling code for it.
"""
from __future__ import annotations

import os
import sys

import torch
from sentence_transformers import SentenceTransformer


class Wrap(torch.nn.Module):
    def __init__(self, st, has_tt):
        super().__init__()
        self.st = st
        self.has_tt = has_tt

    def forward(self, input_ids, attention_mask, token_type_ids=None):
        feats = {"input_ids": input_ids, "attention_mask": attention_mask}
        if self.has_tt and token_type_ids is not None:
            feats["token_type_ids"] = token_type_ids
        return self.st(feats)["sentence_embedding"]


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    st = SentenceTransformer(src, device="cpu").eval()
    tok = st.tokenizer
    has_tt = "token_type_ids" in tok("x")
    ex = tok(["hello world"], return_tensors="pt")
    names = ["input_ids", "attention_mask"] + (["token_type_ids"] if has_tt else [])
    inputs = tuple(ex[n] for n in names)
    fp32 = os.path.join(out, "encoder_fp32.onnx")
    torch.onnx.export(Wrap(st, has_tt), inputs, fp32, input_names=names, output_names=["embedding"],
                      dynamic_axes={**{n: {0: "b", 1: "s"} for n in names}, "embedding": {0: "b"}},
                      opset_version=17, dynamo=False)
    from onnxruntime.quantization import QuantType, quantize_dynamic
    q8 = os.path.join(out, "encoder.onnx")
    quantize_dynamic(fp32, q8, weight_type=QuantType.QInt8, op_types_to_quantize=["MatMul", "Gemm", "Gather"])
    tok.backend_tokenizer.save(os.path.join(out, "tokenizer.json"))
    print(f"fp32 {os.path.getsize(fp32) / 1e6:.1f} MB -> int8 {os.path.getsize(q8) / 1e6:.1f} MB, inputs {names}")
    os.remove(fp32)


if __name__ == "__main__":
    main()
