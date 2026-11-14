#!/usr/bin/env python3
"""Pura Vida, No PII — rule-based PII redactor (standard library only).

Reads test-input.json (or train-input.json when test-input.json is absent) from the
current directory and writes test-output.json / train-output.json next to it.
"""
import json
import os
import re
import unicodedata

# --------------------------------------------------------------------------- helpers
L = "A-Za-zÁÉÍÓÚÑÜáéíóúñü"          # letters incl. Spanish accents
CAP = r"[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]+"  # one capitalised word
CONNECT = r"(?:de|del|de la|de los|de las|y|la|las|los)"


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    """Normalisation mirroring the evaluator: case, accents, separators."""
    return re.sub(r"[^a-z0-9]", "", strip_accents(s).lower())


def accent_insensitive_pattern(word: str) -> str:
    """Regex that matches the word with or without accents, any case."""
    table = {"a": "[aá]", "e": "[eé]", "i": "[ií]", "o": "[oó]", "u": "[uúü]", "n": "[nñ]"}
    out = []
    for ch in strip_accents(word).lower():
        out.append(table.get(ch, re.escape(ch)))
    return "".join(out)


def digit_variants_pattern(digits: str) -> str:
    """Regex matching these digits with any separators (space, dash, dot, parens) between them."""
    return r"(?<!\d)" + r"[\s\-\.\(\)]*".join(re.escape(d) for d in digits) + r"(?!\d)"


# --------------------------------------------------------------------------- structured PII
MONTHS_EN = "january|february|march|april|may|june|july|august|september|october|november|december"
MONTHS_EN_ABBR = "jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
MONTHS_ES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre"
MONTH = rf"(?:{MONTHS_EN}|{MONTHS_EN_ABBR}|{MONTHS_ES})\.?"

RE_EMAIL = re.compile(rf"[{L}0-9._%+\-]+@[{L}0-9.\-]+\.[{L}]{{2,}}")
RE_IBAN = re.compile(r"(?<![A-Z0-9])CR\s?\d{2}(?:[\s\-]?\d{2,4}){4,8}(?![0-9])", re.I)
RE_IBAN_GLUED = re.compile(r"(?<![A-Z0-9])CR\d{16,26}(?![0-9])", re.I)
RE_CEDULA = re.compile(r"(?<![\d\-])\d[\s\-\.]\d{4}[\s\-\.]\d{4}(?![\d\-])")
RE_CEDULA_GLUED = re.compile(r"(?<!\d)\d{9}(?!\d)")
RE_PHONE = re.compile(
    r"(?<![\d\-])(?:\(?\+?506\)?[\s\-\.]?)?\d{4}[\s\-\.]\d{4}(?![\d\-])"
)
RE_PHONE_GLUED = re.compile(r"(?<![\d\-])(?:\+?506)?\d{8}(?![\d\-])")
RE_DATE = re.compile(
    rf"(?<!\w)(?:"
    rf"{MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}"                 # March 26, 1975
    rf"|\d{{1,2}}(?:st|nd|rd|th)?\s+(?:de\s+)?{MONTH},?\s+(?:de\s+|of\s+)?\d{{4}}"  # 26 March 1975 / 26 de marzo de 1975
    rf"|\d{{4}}[\-/\.]\d{{1,2}}[\-/\.]\d{{1,2}}"                        # 1975-03-26
    rf"|\d{{1,2}}[\-/\.]\d{{1,2}}[\-/\.](?:\d{{4}}|\d{{2}})"            # 26/03/1975, 26/03/75
    rf")(?!\w)",
    re.I,
)
# Costa Rican style postal address: street + landmark/house chunk + city
STREET = r"(?:Calle|Avenida|Av\.|Ave\.|Carretera|Ruta|Barrio|Residencial|Urbanizaci[oó]n|Bulevar|Boulevard|Paseo|Apartado|Apdo\.?)"
STOP = r"(?:to|and|for|so|if|as|but|or|which|that|where|before|after|please|in order|until|while|with|by|on|at|from|via|we|you|i|my|our)"
CHUNK = rf"(?:(?!\s{STOP}\b)[^,\n.;])+"            # address chunk: up to , . ; newline or an English function word
RE_ADDRESS = re.compile(rf"\b{STREET}\s+{CHUNK}(?:,\s*{CHUNK})+")
RE_ADDRESS_LANDMARK = re.compile(  # fallback: landmark / directions chunk without a street keyword
    rf"\b(?:\d{{2,4}}\s*(?:metros|m|mts)\s+(?:al\s+)?(?:norte|sur|este|oeste)|(?:Contiguo|Frente|Diagonal|Detr[aá]s|Al lado|Costado)\s+(?:a|al|de|del)\b){CHUNK}(?:,\s*{CHUNK})*",
    re.I,
)
RE_BOOKING = re.compile(r"\bPV-[A-Z0-9]{5}\b")

# --------------------------------------------------------------------------- names
NAME_SEQ = rf"{CAP}(?:(?:\s+{CONNECT})?\s+{CAP}){{0,4}}"
RELATIVES = (r"son|daughter|wife|husband|partner|mother|father|mom|dad|brother|sister|friend|colleague|"
             r"spouse|fianc[eé]e?|boyfriend|girlfriend|cousin|aunt|uncle|niece|nephew|grandmother|grandfather|"
             r"children|child|kid|kids|family member|companion|guest|travel companion|"
             r"hijo|hija|esposa|esposo|madre|padre|hermano|hermana|amigo|amiga|pareja")
NAME_CUES = [
    re.compile(rf"(?:[Mm]y name is|[Mm]e llamo|[Mm]i nombre es|[Ss]oy|[Tt]his is|[Ii] am|[Ii]'m|[Nn]ame:|[Nn]ombre:|[Ss]peaking with|[Ss]igned,?|[Oo]n behalf of|[Ff]or my|[Mm]y colleague)\s+({NAME_SEQ})"),
    re.compile(rf"(?:[Mm]y|[Oo]ur|[Mm]i|[Nn]uestr[oa])\s+(?:{RELATIVES})\s*,?\s+(?:named\s+|called\s+)?({NAME_SEQ})"),
    re.compile(rf"(?:[Mm]r|[Mm]rs|[Mm]s|[Mm]iss|[Dd]r|[Ss]r|[Ss]ra|[Ss]rta|[Dd]on|[Dd]oña)\.?\s+({NAME_SEQ})"),
    re.compile(rf"(?:[Rr]egards|[Bb]est regards|[Kk]ind regards|[Ww]arm regards|[Ss]incerely|[Bb]est|[Tt]hanks|[Tt]hank you|[Cc heers]+|[Ss]aludos|[Aa]tentamente|[Cc]ordialmente|[Gg]racias|[Yy]ours(?: truly| sincerely)?|[Tt]ake care|[Bb]est wishes|[Mm]any thanks|[Aa]ll the best)\s*,?\s*\n+\s*({NAME_SEQ})\s*$", re.M),
    re.compile(rf"^\s*(?:[Hh]i|[Hh]ello|[Dd]ear|[Hh]ola|[Ee]stimad[oa])\s+({NAME_SEQ})\s*[,:!]", re.M),
    re.compile(rf"(?:traveller|traveler|passenger|passengers|guest|guests|contact(?: person)?|under the name(?: of)?|in the name of|booked by|booking for|reservation for|a nombre de|is|are)\s+(?:is\s+|are\s+)?({NAME_SEQ})\s+(?:will|and I|who|is|are|\(|,)"),
]
# Capitalised phrases that are NOT names (organisation, places, generic)
WHITELIST = {
    "pura vida voyages", "pura vida", "costa rica", "san jose", "san josé", "manuel antonio", "arenal", "tortuguero",
    "tamarindo", "monteverde", "puerto viejo", "la fortuna", "playa hermosa", "corcovado", "osa", "guanacaste",
    "limon", "limón", "heredia", "alajuela", "cartago", "puntarenas", "quepos", "escazu", "escazú", "jaco", "jacó",
    "nosara", "santa teresa", "rio celeste", "río celeste", "poas", "poás", "irazu", "irazú", "cahuita",
    "drake bay", "bahia drake", "samara", "sámara", "liberia", "uvita", "dominical", "montezuma", "papagayo",
    "parque central", "parque nacional", "volcan arenal", "volcán arenal", "the", "please", "could", "thank",
    "regards", "best", "sincerely", "hello", "hi", "dear", "we", "i", "my", "our", "it", "this", "there", "no",
    "process", "keep", "to", "you", "if", "a", "for", "the balance", "the refund", "the payment", "the tour",
    "the hotel", "the guide", "wire", "pv", "san", "la", "el", "los", "las", "de", "del", "monday", "tuesday",
    "wednesday", "thursday", "friday", "saturday", "sunday", "national park", "cloud forest", "pacific", "caribbean",
    "central valley", "tempisque", "sarapiqui", "sarapiquí", "golfito", "bocas", "nicoya", "turrialba", "orosi",
    "orosí", "bajos del toro", "la paz", "rincon de la vieja", "rincón de la vieja", "santa elena", "ojochal",
    "tabacon", "tabacón", "sloth", "cano negro", "caño negro", "tenorio", "barva", "braulio carrillo", "chirripo",
    "chirripó", "whatsapp", "sinpe", "iban", "banco nacional", "bac", "scotiabank", "visa", "mastercard",
}
WHITELIST_TOKENS = {"pura", "vida", "voyages", "costa", "rica", "please", "could", "thank", "thanks", "regards",
                    "hello", "dear", "process", "keep", "wire", "transfer", "the", "and", "with", "from", "that",
                    "this", "there", "then", "when", "what", "which", "where", "while", "would", "should", "will",
                    "san", "josé", "jose", "manuel", "antonio", "arenal", "tortuguero", "tamarindo", "monteverde",
                    "heredia", "limón", "limon", "alajuela", "cartago", "puntarenas", "quepos", "escazú", "escazu",
                    "guanacaste", "corcovado", "jacó", "jaco", "nosara", "liberia", "cahuita", "uvita", "montezuma",
                    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "january",
                    "february", "march", "april", "may", "june", "july", "august", "september", "october",
                    "november", "december", "canal", "volcano", "park", "national", "beach", "hotel", "tour",
                    "tours", "excursion", "canopy", "snorkeling", "hike", "shuttle", "voyage", "booking", "refund",
                    "payment", "invoice", "deposit", "complaint", "reference", "urgent", "team", "pacific",
                    "caribbean", "cloud", "forest", "river", "bay", "island", "playa", "parque", "iglesia",
                    "supermercado", "panadería", "panaderia", "calle", "avenida", "central", "whatsapp", "sinpe",
                    "iban", "banco", "nacional", "visa", "mastercard", "mr", "mrs", "ms", "dr", "sr", "sra",
                    "rican", "request", "cancellation", "cancel", "change", "reschedule", "schedule", "date",
                    "dates", "trip", "package", "bill", "billing", "charge", "card", "bank", "account", "receipt",
                    "confirmation", "confirm", "question", "issue", "problem", "service", "guide", "family",
                    "group", "people", "adults", "night", "nights", "day", "days", "week", "morning", "afternoon",
                    "evening", "subject", "update", "priority", "asap", "important", "immediately", "feedback",
                    "review", "hiking", "rafting", "zipline", "zip", "line", "kayak", "kayaking", "surf",
                    "surfing", "diving", "wildlife", "birds", "bird", "turtle", "turtles", "hot", "springs",
                    "waterfall", "coffee", "chocolate", "boat", "catamaran", "sunset", "fishing", "horseback",
                    "riding", "bridges", "hanging", "sloth", "sloths", "jungle", "rainforest", "reserve",
                    "lodge", "resort", "airport", "pickup", "pick", "up", "drop", "off", "transfer", "transport",
                    "itinerary", "reservation", "customer", "support", "agency", "office", "manager", "staff",
                    "driver", "voucher", "ticket", "tickets", "price", "quote", "money", "amount", "total",
                    "balance", "fee", "fees", "cost", "costs", "colones", "dollars", "usd", "crc", "us",
                    "reembolso", "reserva", "pago", "queja", "cambio", "fecha", "urgente", "gracias", "hola",
                    "saludos", "atentamente", "estimado", "estimada", "equipo", "mensaje", "re", "fw", "fwd",
                    "new", "second", "third", "first", "last", "next", "early", "late", "same", "other",
                    "another", "every", "all", "both", "two", "three", "four", "five", "one", "spanish",
                    "english", "american", "european", "canadian", "german", "french", "nicaragua", "panama",
                    "miami", "houston", "new york", "york", "los angeles", "angeles", "london", "madrid", "toronto"}


EDGE_TOKENS = {"hi", "hello", "dear", "hola", "please", "thanks", "thank", "regards", "best", "sincerely", "my",
               "our", "the", "and", "to", "for", "at", "with", "from", "is", "are", "was", "were", "will", "mr",
               "mrs", "ms", "dr", "sr", "sra", "srta", "also", "note", "if", "we", "i", "it", "this", "that",
               "could", "would", "can", "cannot", "so", "but", "or", "in", "on", "of", "by", "as", "a", "an"}


def trim_candidate(cand: str) -> str:
    """Drop whitelisted / function words from both ends of a capitalised run."""
    toks = cand.split()
    while toks and strip_accents(toks[0]).lower() in EDGE_TOKENS | WHITELIST_TOKENS:
        toks.pop(0)
    while toks and strip_accents(toks[-1]).lower() in EDGE_TOKENS | WHITELIST_TOKENS | {"de", "del", "la", "las", "los", "y"}:
        toks.pop()
    return " ".join(toks)


def plausible_name(s: str) -> bool:
    n = strip_accents(s).lower().strip()
    if n in WHITELIST:
        return False
    toks = [t for t in n.split() if t not in {"de", "del", "la", "las", "los", "y"}]
    if not toks:
        return False
    if all(t in WHITELIST_TOKENS for t in toks):
        return False
    return True


class Redactor:
    def __init__(self, text: str):
        self.text = text
        self.names: set[str] = set()
        self.extra_patterns: list[re.Pattern] = []

    # ---- structured ------------------------------------------------------
    def structured(self):
        t = self.text
        self.bookings = RE_BOOKING.findall(t)

        def sub(regex, tag, record=None):
            nonlocal t

            def repl(m):
                val = m.group(0)
                if RE_BOOKING.fullmatch(val):
                    return val
                if record is not None:
                    record(val)
                return tag
            t = regex.sub(repl, t)

        digits_seen: list[str] = []
        sub(RE_EMAIL, "[EMAIL]", lambda v: self.note_email(v))
        sub(RE_IBAN, "[ACCOUNT]", lambda v: digits_seen.append(re.sub(r"\D", "", v)))
        sub(RE_IBAN_GLUED, "[ACCOUNT]", lambda v: digits_seen.append(re.sub(r"\D", "", v)))
        sub(RE_ADDRESS, "[ADDRESS]")
        sub(RE_ADDRESS_LANDMARK, "[ADDRESS]")
        sub(RE_DATE, "[DOB]")
        sub(RE_CEDULA, "[ID]", lambda v: digits_seen.append(re.sub(r"\D", "", v)))
        sub(RE_PHONE, "[PHONE]", lambda v: digits_seen.append(re.sub(r"\D", "", v)))
        sub(RE_CEDULA_GLUED, "[ID]", lambda v: digits_seen.append(v))
        sub(RE_PHONE_GLUED, "[PHONE]", lambda v: digits_seen.append(re.sub(r"\D", "", v)))
        # every other spelling of the same digit strings (glued, spaced, dotted, without +506)
        for d in digits_seen:
            cands = {d}
            if d.startswith("506") and len(d) == 11:
                cands.add(d[3:])
            for c in cands:
                self.extra_patterns.append(re.compile(digit_variants_pattern(c)))
        self.text = t

    def note_email(self, email: str):
        local = email.split("@")[0]
        # local part itself, and its name-like pieces (carlos.solano -> carlos, solano)
        self.extra_patterns.append(re.compile(r"(?<![\w])" + accent_insensitive_pattern(local) + r"(?![\w])", re.I))
        for piece in re.split(r"[._\-+0-9]+", local):
            if len(piece) >= 3 and strip_accents(piece).lower() not in WHITELIST_TOKENS | EDGE_TOKENS:
                self.names.add(piece)

    # ---- names -----------------------------------------------------------
    def find_names(self):
        t = self.text
        for cue in NAME_CUES:
            for m in cue.finditer(t):
                cand = trim_candidate(m.group(1).strip())
                if cand and plausible_name(cand):
                    self.names.add(cand)
        # generic: 2+ capitalised words in a row that are not whitelisted phrases
        for m in re.finditer(rf"(?<![\w\[]){CAP}(?:(?:\s+{CONNECT})?\s+{CAP}){{1,4}}(?![\w\]])", t):
            cand = trim_candidate(m.group(0))
            if cand and plausible_name(cand):
                self.names.add(cand)

    def apply_names(self):
        t = self.text
        # protect multi-word place names (San José, Puerto Viejo, ...) from token-level name removal
        protected: dict[str, str] = {}
        for i, phrase in enumerate(sorted((p for p in WHITELIST if " " in p), key=len, reverse=True)):
            pat = re.compile(r"(?<![\w])" + r"\s+".join(accent_insensitive_pattern(w) for w in phrase.split()) + r"(?![\w])", re.I)

            def keep(m, i=i):
                key = f"\x00P{i}_{len(protected)}\x00"
                protected[key] = m.group(0)
                return key
            t = pat.sub(keep, t)
        tokens: set[str] = set()
        full = sorted(self.names, key=len, reverse=True)
        for name in full:
            t = re.sub(r"(?<![\w])" + r"\s+".join(accent_insensitive_pattern(w) for w in name.split()) + r"(?![\w])",
                       "[NAME]", t, flags=re.I)
            for tok in name.split():
                if len(tok) >= 3 and strip_accents(tok).lower() not in EDGE_TOKENS \
                        and tok.lower() not in {"de", "del", "la", "las", "los", "y"}:
                    tokens.add(tok)
        for tok in sorted(tokens, key=len, reverse=True):
            t = re.sub(r"(?<![\w])" + accent_insensitive_pattern(tok) + r"(?![\w])", "[NAME]", t, flags=re.I)
        for key, val in protected.items():
            t = t.replace(key, val)
        self.text = t

    def apply_extra(self):
        t = self.text
        for p in self.extra_patterns:
            t = p.sub("[REDACTED]", t)
        # collapse accidental doubles like "[NAME] [NAME]"
        t = re.sub(r"\[NAME\](?:\s+\[NAME\])+", "[NAME]", t)
        self.text = t

    def run(self) -> str:
        self.structured()
        self.find_names()
        self.apply_names()
        self.apply_extra()
        return self.text


def redact(text: str) -> str:
    out = Redactor(text).run()
    return out if out.strip() else "[REDACTED]"


def main():
    if os.path.exists("test-input.json"):
        src, dst = "test-input.json", "test-output.json"
    else:
        src, dst = "train-input.json", "train-output.json"
    with open(src, encoding="utf-8") as f:
        docs = json.load(f)["documents"]
    out = {d["id"]: redact(d.get("text") or "") for d in docs}
    with open(dst, "w", encoding="utf-8") as f:
        json.dump({"redacted_documents": out}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
