#!/usr/bin/env python
"""Measure your submission on the public questions the way the platform measures it.

    python local_check.py my_submission            # a folder with main.py and index/
    python local_check.py my_submission.zip        # or the .zip / .tar.gz / .7z / .rar you are about to upload

Four numbers are compared with limits.json: the size of main.py + index/ on disk, the time to
construct Retriever("index"), the 95th-percentile time of one search(question, 3) call, and
Hit@3 (how often the right document is among the 3 you return). The run uses one CPU thread,
no network, and only the libraries of requirements.txt. Timings depend on your machine: keep
headroom.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

RUNNER = r'''
import json, sys, time, traceback
sub, qpath, out, k, warmup = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
import socket
def _no(*a, **kw): raise OSError("network access is disabled")
class _S(socket.socket):
    def connect(self, *a, **kw): _no()
    def connect_ex(self, *a, **kw): _no()
socket.socket = _S; socket.create_connection = _no; socket.getaddrinfo = _no
import os; os.chdir(sub); sys.path.insert(0, sub)
with open(qpath, encoding="utf-8") as f:
    questions = [json.loads(l) for l in f if l.strip()]
t0 = time.perf_counter()
try:
    from main import Retriever
    r = Retriever("index")
except ModuleNotFoundError as e:
    print(f"IMPORT ERROR: '{e.name}' is not in the runtime environment (see requirements.txt).", file=sys.stderr)
    traceback.print_exc(); sys.exit(3)
except Exception:
    traceback.print_exc(); sys.exit(3)
load_s = time.perf_counter() - t0
res = {"load_s": load_s, "lat": [], "ids": {}, "errors": 0, "first_error": None}
for q in questions[:warmup]:
    try: r.search(q["question"], k)
    except Exception: pass
for q in questions:
    t = time.perf_counter()
    try:
        ids = [str(x) for x in list(r.search(q["question"], k))[:k]]
    except Exception as e:
        ids = []; res["errors"] += 1
        if res["first_error"] is None: res["first_error"] = f"{type(e).__name__}: {e}"
    res["lat"].append((time.perf_counter() - t) * 1000.0)
    res["ids"][q["qid"]] = ids
json.dump(res, open(out, "w", encoding="utf-8"))
'''


def fail(msg: str) -> int:
    print(f"\nNOT RUNNABLE: {msg}")
    return 1


def rar_tool() -> str | None:
    """unrar / 7z on the PATH, or WinRAR's UnRAR.exe found through the Windows registry."""
    for name in ("unrar", "7z", "unar"):
        if shutil.which(name):
            return shutil.which(name)
    if sys.platform == "win32":
        try:
            import winreg

            for hive, key, value in ((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WinRAR", "exe64"),
                                     (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WinRAR.exe", "")):
                try:
                    with winreg.OpenKey(hive, key) as k:
                        exe = winreg.QueryValueEx(k, value)[0]
                    cand = os.path.join(os.path.dirname(exe), "UnRAR.exe")
                    if os.path.isfile(cand):
                        return cand
                except OSError:
                    continue
        except ImportError:
            pass
        for p in (r"C:\Program Files\WinRAR\UnRAR.exe", r"C:\Program Files\7-Zip\7z.exe"):
            if os.path.isfile(p):
                return p
    return None


def extract(archive: Path, dest: Path) -> str | None:
    """Unpack a .zip, .tar(.gz/.bz2/.xz), .7z or .rar into dest. Returns a problem message or None."""
    name = archive.name.lower()
    with open(archive, "rb") as f:
        head = f.read(8)
    if head.startswith(b"PK") or name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    elif head.startswith(b"Rar!") or name.endswith(".rar"):
        tool = rar_tool()
        if tool is None:
            return "this is a .rar; install WinRAR or 7-Zip (or 'unrar' on Linux) to check it locally, or zip it"
        try:
            import rarfile
        except ImportError:
            return "this is a .rar; run `pip install rarfile` to check it locally, or zip it"
        rarfile.UNRAR_TOOL = tool
        with rarfile.RarFile(archive) as rf:
            rf.extractall(dest)
    elif head.startswith(b"7z\xbc\xaf") or name.endswith(".7z"):
        try:
            import py7zr
        except ImportError:
            return "this is a .7z; run `pip install py7zr` to check it locally, or zip it"
        with py7zr.SevenZipFile(archive, "r") as sz:
            sz.extractall(dest)
    else:
        import tarfile

        if not tarfile.is_tarfile(archive):
            return "give a folder, or a .zip / .tar.gz / .7z / .rar archive"
        with tarfile.open(archive, "r:*") as tf:
            tf.extractall(dest)
    return None


# Top-level modules importable in the grading environment (requirements.txt and its dependencies).
RUNTIME_MODULES = {
    "Stemmer", "_distutils_hack", "_yaml", "anyio", "bm25s", "click", "cloudpickle", "colorama",
    "coloredlogs", "exceptiongroup", "faiss", "filelock", "flatbuffers", "fsspec", "google", "h11",
    "hf_xet", "httpcore2", "httpx2", "huggingface_hub", "humanfriendly", "idna", "isympy", "jinja2",
    "joblib", "markupsafe", "model2vec", "mpmath", "numpy", "onnxruntime", "packaging", "pip",
    "pkg_resources", "pyreadline3", "readline", "safetensors", "scipy", "setuptools", "sklearn", "sympy",
    "threadpoolctl", "tokenizers", "tomli", "tqdm", "truststore", "typing_extensions", "yaml",
}


def missing_imports(main_py: Path) -> list[str]:
    """Imports of main.py that the grading environment does not have."""
    runtime = RUNTIME_MODULES | set(getattr(sys, "stdlib_module_names", ()))
    try:
        tree = ast.parse(main_py.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    local = {p.stem for p in main_py.parent.glob("*.py")} | {p.name for p in main_py.parent.iterdir() if p.is_dir()}
    return sorted(n for n in names if n not in runtime and n not in local)


def percentile(values: list[float], p: float) -> float:
    s = sorted(values)
    return s[min(len(s) - 1, max(0, int(round(p / 100.0 * (len(s) - 1)))))] if s else float("nan")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    submission = Path(sys.argv[1])
    limits = json.loads((HERE / "limits.json").read_text(encoding="utf-8"))
    questions_path = HERE / "data" / "sample-input.jsonl"
    gold = {}
    for l in (HERE / "data" / "sample-output.jsonl").read_text(encoding="utf-8").splitlines():
        if l.strip():
            rec = json.loads(l)
            gold[rec["qid"]] = rec["doc_id"]
    k = int(limits["k"])

    tmp = Path(tempfile.mkdtemp(prefix="zemi_check_"))
    try:
        root = tmp / "submission"
        if submission.is_dir():
            shutil.copytree(submission, root)
        else:
            problem = extract(submission, root)
            if problem:
                return fail(problem)
        entries = [p for p in root.iterdir() if not p.name.startswith("__MACOSX")]
        if len(entries) == 1 and entries[0].is_dir() and not (root / "main.py").exists():
            root = entries[0]
        if not (root / "main.py").is_file() or not (root / "index").is_dir():
            return fail("main.py and index/ must be at the top level of the submission")

        size_mb = sum(p.stat().st_size for p in root.rglob("*") if p.is_file()) / 1e6
        missing = missing_imports(root / "main.py")
        if missing:
            return fail(f"main.py imports modules that the grading environment does not have: {', '.join(missing)}")

        env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                   ORT_NUM_THREADS="1", TOKENIZERS_PARALLELISM="false", HF_HUB_OFFLINE="1",
                   TRANSFORMERS_OFFLINE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        runner, out = tmp / "_runner.py", tmp / "_result.json"
        runner.write_text(RUNNER, encoding="utf-8")
        proc = subprocess.run([sys.executable, "-I", str(runner), str(root.resolve()), str(questions_path.resolve()),
                               str(out), str(k), str(int(limits["warmup_queries"]))],
                              env=env, cwd=str(tmp), capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=float(limits["wall_s"]))
        if proc.returncode != 0 or not out.exists():
            print(proc.stderr.strip()[-3000:])
            return fail("your Retriever could not be loaded or crashed (see the traceback above)")
        res = json.loads(out.read_text(encoding="utf-8"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    hit = sum(1 for qid, g in gold.items() if g in res["ids"].get(qid, [])[:k]) / max(1, len(gold))
    p95 = percentile(res["lat"], 95)
    rows = [
        ("index size", f"{size_mb:.2f} MB", f"<= {limits['size_mb']} MB", size_mb <= limits["size_mb"]),
        ("load time", f"{res['load_s']:.2f} s", f"<= {limits['load_s']} s", res["load_s"] <= limits["load_s"]),
        ("p95 latency", f"{p95:.1f} ms", f"<= {limits['p95_ms']} ms", p95 <= limits["p95_ms"]),
        (f"hit@{k}", f"{hit:.3f}", f">= {limits['hit_at_k']}", hit >= limits["hit_at_k"]),
    ]
    print(f"\n{'measure':<14}{'yours':>14}{'limit':>14}   result")
    for name, val, lim, ok in rows:
        print(f"{name:<14}{val:>14}{lim:>14}   {'PASS' if ok else 'FAIL'}")
    if res["errors"]:
        print(f"\nsearch() raised on {res['errors']} questions; first: {res['first_error']}")
    passed = all(ok for *_, ok in rows)
    print("\nALL LIMITS PASSED on the sample questions."
          if passed else "\nNOT PASSING: " + ", ".join(name for name, *_, ok in rows if not ok))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
