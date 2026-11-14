# Ruta de las Identidades (Mexico) - record linkage

**Train split: 12,038 / 12,038 pairs, 0 missing, 0 extra.**

| File | What it is |
|---|---|
| `main.py` | The submission. `python main.py` reads `test-input.csv` in the CWD and writes `test-output.json`. `python main.py <in.csv> [<out.json>]` for anything else. Standard library only, about 0.5 s. |
| `tools/check.py` | Self-check: train split, shuffled rows, and 50 injected same-address decoys. |
| `data/` | The practice input and its expected output. |

## How it works

The desks change everything about a reader except the digits in the address.
They swap first and last name, cut names to initials, use nicknames (Pepe/José,
Pancho/Francisco), add typos, drop accents, and reorder and abbreviate the street
(`Retorno` -> `Ret.`, `Interior` -> `Int.`, house number before or after the street).
The house number, interior/building/apartment numbers and ZIP (+4) never change.

So the key is the sorted list of numbers in the address. Records sharing a key are
one person; every cross-record pair in a key group is a match. On the train split:

- all 12,038 true pairs share a key (no digit is ever perturbed),
- no two different people share a key (0 false candidates),
- no key holds two records from the same table, and clusters are size 2 or 3 (one record per table at most),
- no leftover singleton has a near-miss partner (same ZIP and a shared name) in another table.

If the hidden split ever puts two people on the same numbers in the same table,
`main.py` splits that group by name similarity (handles swaps, initials, typos) so
each person keeps at most one record per table.

## Run and check

```
python main.py data/train-input.csv out.json
python tools/check.py data/train-input.csv data/train-output-2.json
```
