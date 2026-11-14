"""gdb script (practice validation only): log the champion's exact inputs and choice.

At each entry to the engine's champion-move routine (offset 0x32a80) dump the
game state, the champion's memory and the true terrain; at the apply-action
call that follows its search (return address offset 0x33464) log the action.
Output: JSON lines to $CHAMP_TRACE.
"""
import json
import os
import struct

import gdb

OUT = open(os.environ.get("CHAMP_TRACE", "/tmp/champ_trace.jsonl"), "a")
BIN = "samoa-linux-x86_64"
base = None


def ints(b, n):
    return list(struct.unpack("<%di" % n, b[: 4 * n]))


def bits(b):
    q = struct.unpack("<4Q", b[:32])
    return [int((q[i >> 6] >> (i & 63)) & 1) for i in range(225)]


class ChampEntry(gdb.Breakpoint):
    def stop(self):
        inf = gdb.selected_inferior()
        g = int(gdb.parse_and_eval("$rdi"))
        st = inf.read_memory(g + 0x728, 0x60).tobytes()
        mem = inf.read_memory(g + 0x788, 2700).tobytes()
        prof = struct.unpack("<i", inf.read_memory(g + 0x121C, 4).tobytes())[0]
        mp = struct.unpack("<Q", st[:8])[0]
        mb = inf.read_memory(mp, 0x3A4 + 900).tobytes()
        p0, p1 = bits(st[8:40]), bits(st[40:72])
        e = ints(st[72:80], 2)
        s = ints(st[80:88], 2)
        cur, rem = ints(st[88:96], 2)
        rec = {
            "t": "state", "profile": prof, "seat": cur, "remaining": rem, "energy": e, "score": s,
            "owner": [0 if p0[i] else (1 if p1[i] else -1) for i in range(225)],
            "blocked": bits(mb[:32]), "w": ints(mb[0x20:], 225), "c": ints(mb[0x3A4:], 225),
            "mem_owner": ints(mem, 225), "mem_w": ints(mem[900:], 225), "mem_c": ints(mem[1800:], 225),
        }
        OUT.write(json.dumps(rec) + "\n")
        OUT.flush()
        return False


class Apply(gdb.Breakpoint):
    def stop(self):
        rsp = int(gdb.parse_and_eval("$rsp"))
        ret = struct.unpack("<Q", gdb.selected_inferior().read_memory(rsp, 8).tobytes())[0]
        if ret == base + 0x33464:
            a = int(gdb.parse_and_eval("$esi")) & 0xFFFFFFFF
            if a >= 1 << 31:
                a -= 1 << 32
            OUT.write(json.dumps({"t": "action", "a": a}) + "\n")
            OUT.flush()
        return False


def on_stop(ev):
    global base
    if base is not None:
        return
    maps = gdb.execute("info proc mappings", to_string=True)
    for line in maps.splitlines():
        if line.strip().endswith(BIN):
            parts = line.split()
            if int(parts[3], 16) == 0:  # file offset 0
                base = int(parts[0], 16)
                break
    if base is None:
        return
    ChampEntry("*%#x" % (base + 0x32A80), internal=True)
    Apply("*%#x" % (base + 0x23AC0), internal=True)


gdb.execute("set logging file /dev/null")
gdb.execute("set logging redirect on")
gdb.execute("set logging enabled on")
gdb.execute("set pagination off")
gdb.execute("set confirm off")
gdb.events.stop.connect(on_stop)
gdb.execute("catch syscall read")
gdb.execute("run")
while base is None:
    gdb.execute("continue")
gdb.execute("delete")
gdb.execute("continue")
