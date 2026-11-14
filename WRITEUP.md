# Pura Vida, No PII — write-up

**Submission:** `main.py` (standard library only, ~0.5 s for 300 documents).

## Approach

A deterministic, rule-based redactor. Every PII category is handled by a regex family written to cover *all* the
variant forms the task lists, and every detected value is then propagated so that no alternative spelling of the
same item survives in the document. Placeholders follow the golden style: `[NAME]`, `[EMAIL]`, `[PHONE]`,
`[ADDRESS]`, `[ID]`, `[DOB]`, `[ACCOUNT]`. Everything that is not PII is left byte-for-byte intact, so the
downstream topic / urgency / booking-reference rules keep working. `PV-#####` references are explicitly protected.

Order of operations per document:

1. **Structured PII** (longest / most specific first so nothing is half-eaten by a looser pattern):
   emails → IBANs (grouped `CR34 0152 …` and glued `CR34…`, length-tolerant) → postal addresses → dates of birth
   (month-name English/Spanish, `dd/mm/yyyy`, ISO, `dd de mes de yyyy`) → cédulas (`1-2345-6789`, spaced, glued 9
   digits) → phones (`+506 8712-3456`, `8712-3456`, `(506) 8712 3456`, glued 8 or 11 digits).
   For each phone / cédula / IBAN the digit string is remembered, and afterwards *any* spelling of those digits
   with any separators (and with or without the `506` prefix) is removed too.
2. **Addresses** start at a street keyword (`Calle`, `Avenida`, `Barrio`, `Residencial`, …) and swallow the
   comma-separated chunks that follow (landmark, house, city), stopping at a sentence end or an English function
   word such as *to* or *and* — this is what lets "…Quepos to our booking…" keep "to our booking". A fallback
   catches landmark-only chunks ("300 metros norte del Parque Central, Heredia", "Frente al …").
3. **Names** are found by cue phrases (*My name is*, *my son/daughter/wife/…*, *Mr./Sra.*, sign-offs such as
   *Regards,* / *Sincerely,* / *Saludos,* followed by a line, greetings *Hi X,*, *X will be the contact person*)
   plus a generic rule for runs of two or more capitalised words that are not a known organisation / place /
   generic phrase (a whitelist of ~300 tokens: *Pura Vida Voyages*, *San José*, *Manuel Antonio*, *Refund Request*,
   …). Function words are trimmed from both ends of a candidate.
4. **Propagation.** Every name token (≥3 letters) is then removed everywhere in the document, case- and
   accent-insensitively, so first names in greetings, signatures or mid-sentence mentions disappear too. The local
   part of every email (`carlos.solano`) and its pieces are treated as name tokens as well. Known multi-word place
   names are shielded during this pass so a traveller called *José* does not destroy *San José*.

## Validation

- `python main.py` next to the training files reproduces the golden `train-output.json` **exactly (20/20)**.
- `check.py` recovers the ground-truth PII spans from the golden file and verifies that none of their variants
  (full value, email local part, individual name tokens, address chunks, digit strings) survives: **0 / 308 leaked**.
- A 300-document fuzz set with randomised templates, sign-offs, relatives, email domains and every phone / cédula /
  DOB / IBAN spelling listed in the task: **privacy 1.000**, and 100 % of topic and urgency sentences plus booking
  references preserved verbatim.
- Hand-written adversarial messages (names mid-sentence, glued digits, multi-line signatures, Spanish dates,
  three-chunk addresses) redact cleanly.

Known trade-off: unknown capitalised place names (e.g. *Puerto Viejo de Talamanca*) may be replaced by `[NAME]`.
That costs nothing on the privacy side and does not touch the keyword-bearing parts of a message.
