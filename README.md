# The Second Lock (Colibrí, Part II)

Branch for the Colibrí prompt-injection challenge from the LMML 2026 hackathon.

- Submission is a JSON list of 1–12 messages, max 2000 characters per message, 15000 characters total.
- The platform replays the chain against Colibrí with both guards active; the chain is the only memory.
- `validate_chain.py` checks a chain file against those limits before you paste it into the platform.
- Keep the final working chain in `chain.json` (organisers may ask for it).
