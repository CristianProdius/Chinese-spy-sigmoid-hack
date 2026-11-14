import sys, os
from huggingface_hub import hf_hub_download
out = sys.argv[1]
for repo, files in {"Snowflake/snowflake-arctic-embed-xs":["onnx/model_quantized.onnx","onnx/model.onnx","tokenizer.json"],
 "sentence-transformers/static-retrieval-mrl-en-v1":["0_StaticEmbedding/model.safetensors","0_StaticEmbedding/tokenizer.json"]}.items():
    for f in files:
        p = hf_hub_download(repo, f, cache_dir=out); print(repo, f, os.path.getsize(p)//1024, "KB")
