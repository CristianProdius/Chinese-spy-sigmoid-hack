"""Run the task's evaluation_script.py unchanged, with only llama.cpp's thread counts capped.

On a loaded box llama.cpp's default n_threads_batch (= all cores) spin-waits and the eval takes an hour.
Thread counts do not change llama.cpp's results (each output row is reduced by one thread).

  python official.py <adapter.gguf> <out.json> [threads] [--data DIR]
"""
import sys

from common import TASK  # noqa: F401  (puts the task folder on sys.path)

import evaluation_script as ev
import llama_cpp

NT = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 4
_Llama = llama_cpp.Llama


class Llama(_Llama):
    def __init__(self, *a, **k):
        k["n_threads"] = NT
        k["n_threads_batch"] = NT
        super().__init__(*a, **k)


llama_cpp.Llama = Llama
argv = ["evaluation_script.py", "--model", sys.argv[1], "--out", sys.argv[2]]
if "--data" in sys.argv:
    argv += ["--data", sys.argv[sys.argv.index("--data") + 1]]
sys.argv = argv
sys.exit(ev.main())
