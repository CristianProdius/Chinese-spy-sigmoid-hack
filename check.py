"""Local scorer: exact-match vs golden + privacy check over all PII variants."""
import json, re, difflib, unicodedata
def strip(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
def norm(s): return re.sub(r"[^a-z0-9]", "", strip(s).lower())
I={d['id']:d['text'] for d in json.load(open('train-input.json'))['documents']}
G=json.load(open('train-output.golden.json'))['redacted_documents']
M=json.load(open('train-output.json'))['redacted_documents']
exact=0; items=0; leaked=0
for i,src in I.items():
    g,m=G[i],M[i]
    if g==m: exact+=1
    else:
        print('DIFF',i); 
        for l in difflib.unified_diff(g.splitlines(),m.splitlines(),lineterm='',n=0): print('   ',l)
    # ground-truth PII = spans golden replaced; recover them by aligning
    parts=re.split(r'\[[A-Z]+\]',g)
    rx='(.+?)'.join(re.escape(p) for p in parts)
    mm=re.fullmatch(rx,src,re.S); assert mm, i
    pii=list(mm.groups())
    nm=norm(m)
    for p in pii:
        p=p.strip(' .,;')
        variants={p}
        if '@' in p: variants.add(p.split('@')[0])
        for w in re.split(r'[\s,]+',p):
            if len(w)>=3 and not w.isdigit() and w.lower() not in {'de','del','la','las','los','metros','norte','sur','este','oeste','frente','contiguo','al','a','avenida','calle'}: variants.add(w)
        for v in variants:
            items+=1
            if norm(v) and norm(v) in nm: leaked+=1; print('LEAK',i,repr(v))
print(f'exact match {exact}/{len(I)}   leaked variants {leaked}/{items}')
