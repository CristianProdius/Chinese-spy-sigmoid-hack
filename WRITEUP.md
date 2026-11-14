# The Knots You Cannot Read — write-up

**Flag:** `SIGMOID_PROVENANCE`

## 1. Confirm the model is what it claims

`model.safetensors` holds three tensors:

| tensor | shape |
|---|---|
| `embedding.weight` | 256 × 32 |
| `classifier.weight` | 3 × 32 |
| `classifier.bias` | 3 |

So the architecture is: byte → 32-d embedding → mean-pool over the 64 characters → linear layer → 3 logits.
Re-implementing that in numpy and scoring `corpus.csv` (labels in alphabetical order:
antisuyu, chinchaysuyu, qullasuyu) gives **95.4 % accuracy**. The classifier is honest.

## 2. Where behaviour cannot reach

The corpus uses only 17 distinct bytes (space and 16 lowercase letters), and the model is documented as reading
ASCII. Every embedding row for a byte ≥ 128 is therefore dead weight: no legitimate input ever indexes it, so no
amount of probing the model's predictions can expose what is stored there. Those rows look like ordinary
N(0, 1) initialisation noise, which is why they survived eight months in production.

## 3. Finding the payload

Trained float32 weights have effectively random low mantissa bits. Scanning every float in the artifact for a
zeroed low 16 bits turns up exactly 18 hits, all in **row 128** (the first non-ASCII byte), columns 0–17:

```
0xbd340000 0xbd5c0000 0xbd640000 ... 0xbd6c0000
```

Multiplying those values by 1024 gives exact integers, −45 … −63. They are not text, and `strings` cannot see
them, but adding 128 maps each one onto an ASCII code:

```
value * 1024 + 128  →  83 73 71 77 79 73 68 95 80 82 79 86 69 78 65 78 67 69
                    →  S  I  G  M  O  I  D  _  P  R  O  V  E  N  A  N  C  E
```

The remaining 14 entries of row 128 are ordinary noise, so the row's norm and mean stay unremarkable.

Checks that nothing else is planted: the LSB plane of the whole embedding is incompressible (ratio 1.01, same as
random), the projection of the embedding onto the classifier's 29-dimensional null space has a flat spectrum,
and no other row contains integer-quantised values.

## 4. Extraction code

See [`extract.py`](extract.py):

```python
w = load_file("model.safetensors"); E = w["embedding.weight"]
clean = np.argwhere((E.view(np.uint32) & 0xFFFF) == 0)       # -> all in row 128
flag = "".join(chr(int(round(v * 1024)) + 128) for v in E[128, :len(clean)])
print(flag)                                                  # SIGMOID_PROVENANCE
```
