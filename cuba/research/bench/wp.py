import unicodedata, time, sys, re
def load_vocab(p):
    with open(p, encoding="utf-8") as f:
        return {l.rstrip("\n"): i for i, l in enumerate(f)}
def _is_punc(ch):
    cp = ord(ch)
    if (33 <= cp <= 47) or (58 <= cp <= 64) or (91 <= cp <= 96) or (123 <= cp <= 126): return True
    return unicodedata.category(ch).startswith("P")
def _is_cjk(cp):
    return (0x4E00<=cp<=0x9FFF) or (0x3400<=cp<=0x4DBF) or (0x20000<=cp<=0x2A6DF) or (0x2A700<=cp<=0x2B73F) or (0x2B740<=cp<=0x2B81F) or (0x2B820<=cp<=0x2CEAF) or (0xF900<=cp<=0xFAFF) or (0x2F800<=cp<=0x2FA1F)
def basic(text):
    out = []
    for ch in text:
        cp = ord(ch)
        if cp == 0 or cp == 0xFFFD or (unicodedata.category(ch) in ("Cc","Cf") and ch not in "\t\n\r"): continue
        if _is_cjk(cp): out.append(" "+ch+" ")
        elif ch in " \t\n\r" or unicodedata.category(ch) == "Zs": out.append(" ")
        else: out.append(ch)
    toks = []
    for w in "".join(out).split():
        w = unicodedata.normalize("NFD", w.lower())
        w = "".join(c for c in w if unicodedata.category(c) != "Mn")
        cur = ""
        for c in w:
            if _is_punc(c):
                if cur: toks.append(cur); cur = ""
                toks.append(c)
            else: cur += c
        if cur: toks.append(cur)
    return toks
def wordpiece(word, vocab, unk="[UNK]", maxlen=100):
    if len(word) > maxlen: return [unk]
    out, start = [], 0
    while start < len(word):
        end, cur = len(word), None
        while start < end:
            s = word[start:end]
            if start > 0: s = "##" + s
            if s in vocab: cur = s; break
            end -= 1
        if cur is None: return [unk]
        out.append(cur); start = end
    return out
def encode(text, vocab):
    return [vocab[p] for w in basic(text) for p in wordpiece(w, vocab)]
