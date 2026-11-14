"""Zip a submission folder (main.py + index/) into work/subs/<name>.zip."""
import os, sys, zipfile
src, name = sys.argv[1], sys.argv[2]
out = os.path.join(os.path.dirname(__file__), "..", "work", "subs", name + ".zip")
os.makedirs(os.path.dirname(out), exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(src, "main.py"), "main.py")
    for root, _, files in os.walk(os.path.join(src, "index")):
        for f in sorted(files):
            p = os.path.join(root, f); z.write(p, os.path.relpath(p, src))
print(out, os.path.getsize(out) / 1e6, "MB zipped")
