# Looks Good to Me! — Bogotá Sound Check (Colombia, AI Security, Easy)

**Flag: `SIGMOID_DATA_SANITIZATION`**

Reproduce: `python solve.py data/reviews.json` (downloads the 2.4 MB public source dump on first run).

## The data
`reviews.json` holds 1,000 `trusted_reference` reviews, 1,200 `samples` (with `sample_index`),
and an `archive_note`. Every record carries a 64-hex `archive_tag` ("seal"). The note says:
sort the altered records' `sample_index` values, join with commas, SHA-256 that string, XOR the
32-byte digest against every seal, strip trailing zero bytes; one seal becomes the message.

## Finding the altered records
Every review in the file is a verbatim copy from the public Amazon *Musical Instruments 5-core*
dump (10,261 reviews, snap.stanford.edu), with two cosmetic changes applied uniformly to both
sets: straight apostrophes became `’` and hyphens became `–`. Those are decoys. Two real kinds of
tampering hide in `samples`:

1. **Invisible text edits (12 records).** A zero-width space (U+200B) or a Cyrillic look-alike
   letter (а е о с) was planted inside one of the first three words. The trusted set contains
   none of these characters, so "characters absent from trusted text" is an exact detector.
   Indices: 36, 119, 216, 273, 357, 367, 462, 478, 513, 685, 752, 1199.

2. **Rating nudges (12 records).** Ratings were moved by one star between 3 and 4. The text is
   untouched, and a 3-vs-4 review is as ambiguous as the trusted set's own noise, so no classifier
   (we tried TF-IDF and a 72B LLM) separates them cleanly. Matching each review back to its
   source record by normalised text and comparing `overall` gives the exact set:
   112, 198, 347, 371, 432, 582, 622, 633, 661, 1018, 1061, 1112
   (4→3: 112, 198, 371, 432, 633, 1061; 3→4: 347, 582, 622, 661, 1018, 1112).
   The trusted set matches its source perfectly, which confirms it is clean.

Neither dozen decodes on its own. Their union does.

## Recovering the message
```
key  = "36,112,119,198,216,273,347,357,367,371,432,462,478,513,582,622,633,661,685,752,1018,1061,1112,1199"
mask = sha256(key)            # 32 bytes
```
XOR-ing the mask against all 2,200 seals leaves exactly one printable result, in the seal of
trusted review 613: `SIGMOID_DATA_SANITIZATION`.

## Dead ends worth recording
- Brute force over the seals: any ≤3 arbitrary indices, the 12 text-edited plus ≤3 extras,
  powersets of every rating/text mismatch an LLM could find. The real set has 24 members, so
  subset search without the second signal was hopeless.
- Alternate readings of the note (string sort, JSON list, hex digest as mask) all fail; the
  note is literal.
- The ZIP has no comment, extra fields, or trailing data. "Archive metadata" means the tags.
