import sys
from huggingface_hub import hf_hub_download, list_repo_files
out = sys.argv[1]
spec = {
 "Xenova/all-MiniLM-L6-v2": ["onnx/model.onnx","onnx/model_quantized.onnx","tokenizer.json"],
 "Xenova/bge-small-en-v1.5": ["onnx/model.onnx","onnx/model_quantized.onnx","tokenizer.json"],
 "Snowflake/snowflake-arctic-embed-xs": None,
 "minishlab/potion-retrieval-32M": ["model.safetensors","tokenizer.json","config.json"],
 "minishlab/potion-base-8M": ["model.safetensors","tokenizer.json","config.json"],
 "sentence-transformers/static-retrieval-mrl-en-v1": None,
}
for repo, files in spec.items():
    if files is None:
        fl = list_repo_files(repo); print(repo, fl)
        continue
    for f in files:
        p = hf_hub_download(repo, f, cache_dir=out)
        import os; print(repo, f, os.path.getsize(p)//1024, "KB")
